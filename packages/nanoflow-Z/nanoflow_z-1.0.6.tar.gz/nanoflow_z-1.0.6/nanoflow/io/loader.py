
import threading
import queue
from safetensors.torch import safe_open

class AsyncLoader:
    def __init__(self, safetensors_file, layer_names, queue_size=2):
        self.safetensors_file = safetensors_file
        self.layer_names = layer_names
        self.queue = queue.Queue(maxsize=queue_size)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._worker)

    def start(self):
        self.thread.start()

    def join(self):
        self.stop_event.set()
        self.thread.join()

    def _worker(self):
        for name in self.layer_names:
            if self.stop_event.is_set(): break
            # Simulation chargement
            data = {"name": name, "tensors": {}} 
            self.queue.put(data)

    def get_layer(self, name):
        return self.queue.get()
