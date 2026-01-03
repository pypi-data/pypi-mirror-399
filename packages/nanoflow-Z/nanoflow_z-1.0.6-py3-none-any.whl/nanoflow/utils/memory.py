
import gc
import torch

class MemoryGuardian:
    def flush(self):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

guardian = MemoryGuardian()
