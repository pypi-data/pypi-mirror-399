
import gc
import torch
import psutil
import os

class MemoryGuardian:
    def __init__(self, limit_gb=1.5):
        self.limit_gb = limit_gb

    def get_usage(self):
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 ** 3)

    def check(self):
        usage = self.get_usage()
        if usage > self.limit_gb:
            self.flush()
            # On revérifie après nettoyage
            if self.get_usage() > self.limit_gb:
                print(f"⚠️ Warning NanoFlow: RAM à {usage:.2f} GB (Target: {self.limit_gb} GB)")

    def flush(self):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# Instance globale configurée sur 1.5 GB comme demandé
guardian = MemoryGuardian(limit_gb=1.5)
