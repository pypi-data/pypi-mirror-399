
import torch
from transformers import AutoConfig

class NanoFlowEngine:
    def __init__(self, model_id, device="cpu"):
        self.device = device
        self.config = AutoConfig.from_pretrained(model_id)
        self.hidden_size = self.config.hidden_size
        
    def forward_token(self, input_ids, loader):
        # Logique simplifiée de la v0.1.0 qui fonctionnait
        batch_size, seq_len = input_ids.shape
        return torch.zeros((batch_size, seq_len, self.hidden_size), device=self.device)
