
import torch
import torch.nn.functional as F
from transformers import AutoConfig
from nanoflow.utils.memory import MemoryGuardian

def manual_rms_norm(x, weight, eps=1e-6):
    return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps) * weight

def rotate_half(x):
    """Rotates half the hidden dims of the input."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)

def apply_rotary_pos_emb(q, k, cos, sin):
    # q, k: [Batch, Heads, Seq, HeadDim]
    # cos, sin: [1, 1, Seq, HeadDim]
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed

def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1:
        return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)

class NanoFlowEngine:
    def __init__(self, model_id):
        self.config = AutoConfig.from_pretrained(model_id)
        self.guardian = MemoryGuardian()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        print(f"Config Loaded: Hidden={self.config.hidden_size}, Heads={self.config.num_attention_heads}, RoPE Theta={getattr(self.config, "rope_theta", "Default")}")

    def forward_token(self, hidden_states, loader):
        hidden_states = hidden_states.to(self.device)

        while True:
            weights = loader.get_next()
            if weights is None:
                break

            # Infer group_name
            key = next(iter(weights.keys()))
            if "embed_tokens" in key:
                group_name = "embed_tokens"
            elif "layers" in key:
                group_name = "layers"
            elif "norm" in key:
                group_name = "norm"
            else:
                group_name = "unknown"

            # Move to device
            for k in list(weights.keys()):
                weights[k] = weights[k].to(device=self.device, dtype=self.dtype)

            try:
                if "embed_tokens" in group_name:
                    weight = next(v for k,v in weights.items() if "weight" in k)
                    hidden_states = F.embedding(hidden_states, weight)

                elif "layers" in group_name:
                    def get_w(partial_name):
                        for k, v in weights.items():
                            if partial_name in k: return v
                        return None

                    input_layernorm = get_w("input_layernorm.weight")
                    post_attention_layernorm = get_w("post_attention_layernorm.weight")
                    
                    q_w = get_w("q_proj.weight")
                    k_w = get_w("k_proj.weight")
                    v_w = get_w("v_proj.weight")
                    o_w = get_w("o_proj.weight")
                    
                    # Check for biases (Qwen2.5 usually has QKV biases)
                    q_b = get_w("q_proj.bias")
                    k_b = get_w("k_proj.bias")
                    v_b = get_w("v_proj.bias")
                    o_b = get_w("o_proj.bias")

                    gate_w = get_w("gate_proj.weight")
                    up_w = get_w("up_proj.weight")
                    down_w = get_w("down_proj.weight")
                    # MLP biases (usually None for Qwen/Llama, but good to have logic)
                    gate_b = get_w("gate_proj.bias")
                    up_b = get_w("up_proj.bias")
                    down_b = get_w("down_proj.bias")

                    # --- Attention Block ---
                    residual = hidden_states
                    norm_out = manual_rms_norm(hidden_states, input_layernorm, self.config.rms_norm_eps)

                    # Linear Projections with Bias support
                    q = F.linear(norm_out, q_w, q_b)
                    k = F.linear(norm_out, k_w, k_b)
                    v = F.linear(norm_out, v_w, v_b)

                    bsz, seq_len, _ = hidden_states.shape
                    num_heads = self.config.num_attention_heads
                    num_kv_heads = getattr(self.config, "num_key_value_heads", num_heads)
                    if num_kv_heads is None: num_kv_heads = num_heads
                    head_dim = self.config.hidden_size // num_heads

                    q = q.view(bsz, seq_len, num_heads, head_dim)
                    k = k.view(bsz, seq_len, num_kv_heads, head_dim)
                    v = v.view(bsz, seq_len, num_kv_heads, head_dim)

                    # RoPE
                    rope_theta = getattr(self.config, "rope_theta", 10000.0)
                    inv_freq = 1.0 / (rope_theta ** (torch.arange(0, head_dim, 2, device=self.device).float() / head_dim))
                    t = torch.arange(seq_len, device=self.device, dtype=inv_freq.dtype)
                    freqs = torch.outer(t, inv_freq)
                    emb = torch.cat((freqs, freqs), dim=-1)
                    
                    cos = emb.cos()[None, None, :, :]
                    sin = emb.sin()[None, None, :, :]

                    q = q.transpose(1, 2)
                    k = k.transpose(1, 2)
                    v = v.transpose(1, 2)

                    q, k = apply_rotary_pos_emb(q, k, cos, sin)

                    if num_kv_heads < num_heads:
                        n_rep = num_heads // num_kv_heads
                        k = repeat_kv(k, n_rep)
                        v = repeat_kv(v, n_rep)

                    attn_output = F.scaled_dot_product_attention(q, k, v, is_causal=True)
                    attn_output = attn_output.transpose(1, 2).contiguous().view(bsz, seq_len, -1)

                    hidden_states = F.linear(attn_output, o_w, o_b) + residual

                    # --- MLP Block ---
                    residual = hidden_states
                    norm_out = manual_rms_norm(hidden_states, post_attention_layernorm, self.config.rms_norm_eps)

                    gate = F.linear(norm_out, gate_w, gate_b)
                    up = F.linear(norm_out, up_w, up_b)
                    swiglu = F.silu(gate) * up
                    hidden_states = F.linear(swiglu, down_w, down_b) + residual

                elif "norm" in group_name:
                    weight = next(v for k,v in weights.items() if "weight" in k)
                    hidden_states = manual_rms_norm(hidden_states, weight, self.config.rms_norm_eps)

            finally:
                del weights
                self.guardian.flush()

        return hidden_states
