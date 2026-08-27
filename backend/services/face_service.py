import importlib.util
import os
import tempfile
from PIL import Image
import numpy as np
from config import Config


class FaceServiceUnavailable(RuntimeError):
    pass


class FaceProcessingError(RuntimeError):
    pass


def deepface_available() -> bool:
    return importlib.util.find_spec('deepface') is not None


def face_backend_status() -> dict:
    if not Config.AI_ENABLED:
        return {'enabled': False, 'backend': 'disabled', 'available': False}
    available = deepface_available()
    return {
        'enabled': True,
        'backend': 'DeepFace' if available else 'unavailable',
        'available': available,
        'model': Config.FACE_MODEL,
        'detector': Config.FACE_DETECTOR,
    }


def _temp_image(image: Image.Image) -> str:
    handle = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    handle.close()
    image.convert('RGB').save(handle.name, format='JPEG', quality=92)
    return handle.name


def extract_embeddings(image: Image.Image) -> list[dict]:
    if not Config.AI_ENABLED:
        raise FaceServiceUnavailable('AI face processing is disabled in the current configuration.')
    if not deepface_available():
        raise FaceServiceUnavailable('DeepFace is not installed. Install backend/requirements-ai.txt and restart the API.')

    path = _temp_image(image)
    try:
        from deepface import DeepFace
        try:
            results = DeepFace.represent(
                img_path=path,
                model_name=Config.FACE_MODEL,
                detector_backend=Config.FACE_DETECTOR,
                enforce_detection=True,
                align=True,
            )
        except ValueError:
            # DeepFace commonly raises ValueError when no valid face can be detected.
            return []
        except Exception as exc:
            raise FaceProcessingError('The face-recognition backend could not process the image.') from exc

        output = []
        for index, item in enumerate(results or []):
            embedding = [float(x) for x in item.get('embedding', [])]
            if not embedding:
                continue
            output.append({
                'face_index': index,
                'embedding': embedding,
                'confidence': float(item.get('face_confidence') or 0),
                'box': item.get('facial_area') or {},
            })
        return output
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def cosine_similarity(a: list[float], b: list[float]) -> float:
    left = np.asarray(a, dtype=np.float32)
    right = np.asarray(b, dtype=np.float32)
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    return float(np.dot(left, right) / denominator) if denominator else 0.0


def match_embeddings(query_embedding: list[float], rows: list[dict], threshold: float | None = None) -> list[dict]:
    limit = Config.FACE_COSINE_THRESHOLD if threshold is None else threshold
    best_by_image: dict[str, dict] = {}
    for row in rows:
        embedding = row.get('embedding') or []
        score = cosine_similarity(query_embedding, embedding)
        if score < limit:
            continue
        current = best_by_image.get(row['image_id'])
        if current is None or score > current['similarity']:
            best_by_image[row['image_id']] = {**row, 'similarity': score}
    return sorted(best_by_image.values(), key=lambda item: item['similarity'], reverse=True)
