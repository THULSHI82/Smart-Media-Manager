import io
from pathlib import Path
import requests
from PIL import Image
from config import Config


def load_pil(image_url: str, public_id: str | None = None) -> Image.Image:
    if Config.STORAGE_BACKEND == 'local' and public_id:
        path = Path(Config.LOCAL_UPLOAD_DIR) / public_id
        return Image.open(path).convert('RGB')
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert('RGB')
