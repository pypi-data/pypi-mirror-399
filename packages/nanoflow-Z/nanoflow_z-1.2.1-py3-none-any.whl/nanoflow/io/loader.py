import threading, queue
class AsyncLoader:
    def __init__(self, safetensors_file, layer_names, queue_size=2):
        self.safetensors_file = safetensors_file
        self.queue = queue.Queue(maxsize=queue_size)
    def start(self): pass
    def join(self): pass
    def get_layer(self, name): return None
