
import os
import requests
import gc
from huggingface_hub import HfApi, hf_hub_url
from tqdm import tqdm

class NanoDownloader:
    @staticmethod
    def download_model(repo_id, local_dir="models"):
        api = HfApi()
        try:
            files = api.list_repo_files(repo_id=repo_id)
        except Exception:
            return None
        
        extensions = ['.safetensors', '.json', '.txt', '.model', '.py']
        target_files = [f for f in files if any(f.endswith(ext) for ext in extensions)]
        
        save_path = os.path.join(local_dir, repo_id.replace("/", "_"))
        os.makedirs(save_path, exist_ok=True)
        
        print(f"⬇️ ZERO-RAM DOWNLOAD : {repo_id}")
        
        for filename in target_files:
            file_path = os.path.join(save_path, filename)
            if os.path.exists(file_path): continue
                
            url = hf_hub_url(repo_id=repo_id, filename=filename)
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    with open(file_path, 'wb') as f, tqdm(total=total_size, unit='iB', unit_scale=True) as bar:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
                                f.flush()
                                os.fsync(f.fileno())
                del r; gc.collect()
            except Exception as e: print(e)
            
        return save_path
