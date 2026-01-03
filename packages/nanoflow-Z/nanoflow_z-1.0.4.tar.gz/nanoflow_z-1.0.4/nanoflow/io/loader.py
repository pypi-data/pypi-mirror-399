
import threading
import queue
import torch
from safetensors import safe_open
from nanoflow.utils.memory import MemoryGuardian

class AsyncLoader(threading.Thread):
    def __init__(self, model_path, layer_names):
        super().__init__()
        self.model_path = model_path
        self.layer_names = layer_names
        # Internal queue with maxsize=1 to create backpressure
        self.queue = queue.Queue(maxsize=1)
        self.guardian = MemoryGuardian()
        self.daemon = True

    def run(self):
        try:
            with safe_open(self.model_path, framework="pt", device="cpu") as f:
                all_keys = f.keys()
                for name in self.layer_names:
                    weights = {}
                    # Strict prefix matching to avoid model.layers.1 matching model.layers.10
                    # We check if key starts with "name." (e.g. "model.layers.1.")
                    relevant_keys = [k for k in all_keys if k.startswith(name + ".")]

                    if not relevant_keys:
                        continue

                    for k in relevant_keys:
                        weights[k] = f.get_tensor(k)

                    self.queue.put(weights)

                    del weights
                    self.guardian.flush()

        except Exception as e:
            print(f"Error in AsyncLoader: {e}")
        finally:
            self.queue.put(None)
            self.guardian.flush()

    def get_next(self):
        return self.queue.get()
