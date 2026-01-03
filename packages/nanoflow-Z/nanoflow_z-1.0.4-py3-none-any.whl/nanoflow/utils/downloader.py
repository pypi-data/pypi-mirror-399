
import os
from huggingface_hub import snapshot_download

def smart_download(repo_id):
    print(f"⬇️ Downloading {repo_id}...")
    try:
        path = snapshot_download(repo_id=repo_id)
        # Return path to model.safetensors if it exists, else folder
        safe = os.path.join(path, "model.safetensors")
        if os.path.exists(safe):
            return safe
        return path
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return None
