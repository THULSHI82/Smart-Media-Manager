from pathlib import Path
from PIL import Image
from config import Config

_model = None


def _heuristic_category(image: Image.Image, face_count: int) -> tuple[str, float]:
    ratio = image.width / max(image.height, 1)
    if face_count >= 8:
        return 'Crowd', 0.72
    if 3 <= face_count < 8:
        return 'Group', 0.70
    if face_count == 1 and ratio < 1.15:
        return 'Portrait', 0.68
    if ratio > 1.65:
        return 'Stage', 0.55
    return 'General', 0.50


def _tensorflow_category(image: Image.Image) -> tuple[str, float] | None:
    global _model
    path = Config.CLASSIFICATION_MODEL_PATH
    if not path or not Path(path).exists():
        return None
    try:
        import numpy as np
        import tensorflow as tf
        if _model is None:
            _model = tf.keras.models.load_model(path)
        resized = image.resize((224, 224)).convert('RGB')
        batch = np.expand_dims(np.asarray(resized, dtype='float32') / 255.0, axis=0)
        predictions = _model.predict(batch, verbose=0)[0]
        labels = ['Stage', 'Crowd', 'Group', 'Dance', 'Sports', 'General']
        index = int(np.argmax(predictions))
        return labels[index], float(predictions[index])
    except Exception:
        return None


def classify_image(image: Image.Image, face_count: int = 0) -> dict:
    result = _tensorflow_category(image) if Config.CLASSIFIER_BACKEND == 'tensorflow' else None
    backend = 'tensorflow' if result else 'heuristic'
    if result is None:
        result = _heuristic_category(image, face_count)
    label, confidence = result
    return {'label': label, 'confidence': round(confidence, 4), 'backend': backend}
