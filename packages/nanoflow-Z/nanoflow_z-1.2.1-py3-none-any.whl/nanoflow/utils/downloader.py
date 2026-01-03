
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
        except: return None
        
        # CORRECTION ICI : Ajout de '.py' et '.bin'
        extensions = ['.safetensors', '.json', '.txt', '.model', '.py', '.bin']
        targets = [f for f in files if any(f.endswith(x) for x in extensions)]
        
        path = os.path.join(local_dir, repo_id.replace("/", "_"))
        os.makedirs(path, exist_ok=True)
        
        print(f"⬇️ DOWNLOAD v1.2.1: {repo_id}")
        for filename in targets:
            fp = os.path.join(path, filename)
            
            # CORRECTION ICI : Création des sous-dossiers (pour éviter l'erreur 1_Pooling)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            
            if os.path.exists(fp): continue
            
            url = hf_hub_url(repo_id=repo_id, filename=filename)
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    total = int(r.headers.get('content-length', 0))
                    with open(fp, 'wb') as f, tqdm(total=total, unit='iB', unit_scale=True, desc=filename) as bar:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
                                f.flush()
                                os.fsync(f.fileno())
                del r; gc.collect()
            except Exception as e: print(f"⚠️ Erreur sur {filename}: {e}")
        return path
