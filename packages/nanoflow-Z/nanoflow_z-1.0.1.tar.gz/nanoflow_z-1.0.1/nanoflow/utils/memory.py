
import gc
import os
import platform
import ctypes
import psutil

try:
    import torch
except ImportError:
    torch = None

class MemoryGuardian:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MemoryGuardian, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.os_type = platform.system()
            self.initialized = True

    def get_ram_usage(self):
        """Returns the current process RAM usage in MB."""
        process = psutil.Process(os.getpid())
        ram_usage_mb = process.memory_info().rss / (1024 * 1024)
        return ram_usage_mb

    def flush(self):
        """Performs aggressive memory cleanup."""
        # 1. Python Garbage Collection
        gc.collect()

        # 2. PyTorch CUDA Cache
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()

        # 3. OS-specific memory trimming
        try:
            if self.os_type == "Linux":
                # Use libc to trim memory (malloc_trim)
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            elif self.os_type == "Windows":
                # Use psapi to empty working set
                ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except Exception:
            # Silently fail if OS specific calls don't work
            pass

# Create global instance required by __init__.py
guardian = MemoryGuardian()
