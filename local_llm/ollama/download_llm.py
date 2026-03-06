import huggingface_hub as hf_hub

from .config import model_id, model_path

hf_hub.snapshot_download(model_id, local_dir=model_path)
