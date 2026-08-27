from PIL import Image
import imagehash
from config import Config


def compute_phash(image: Image.Image) -> str:
    return str(imagehash.phash(image))


def closest_duplicate(candidate_hash: str, known: list[dict], threshold: int | None = None) -> dict | None:
    limit = Config.DUPLICATE_HASH_DISTANCE if threshold is None else threshold
    candidate = imagehash.hex_to_hash(candidate_hash)
    best = None
    for item in known:
        value = item.get('perceptual_hash')
        if not value:
            continue
        distance = candidate - imagehash.hex_to_hash(value)
        if distance <= limit and (best is None or distance < best['distance']):
            best = {'image_id': item['id'], 'distance': int(distance)}
    return best
