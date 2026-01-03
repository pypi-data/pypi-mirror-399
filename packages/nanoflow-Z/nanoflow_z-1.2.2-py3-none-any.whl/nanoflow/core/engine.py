import torch
from transformers import AutoConfig
class NanoFlowEngine:
    def __init__(self, model_path, device="cpu"):
        self.device = device
        # Le fix vital : trust_remote_code=True
        self.config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        self.hidden_size = self.config.hidden_size
    def forward_token(self, input_ids, loader):
        return torch.zeros((input_ids.shape[0], input_ids.shape[1], self.hidden_size), device=self.device)
