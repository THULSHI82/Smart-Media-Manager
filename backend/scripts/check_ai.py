import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import Config


def present(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


if __name__ == '__main__':
    classifier_path = Path(Config.CLASSIFICATION_MODEL_PATH) if Config.CLASSIFICATION_MODEL_PATH else None
    status = {
        'AI_ENABLED': Config.AI_ENABLED,
        'DeepFace installed': present('deepface'),
        'TensorFlow installed': present('tensorflow'),
        'Face model': Config.FACE_MODEL,
        'Face detector': Config.FACE_DETECTOR,
        'Classifier backend': Config.CLASSIFIER_BACKEND,
        'Classifier model exists': bool(classifier_path and classifier_path.exists()),
    }
    for key, value in status.items():
        print(f'{key}: {value}')
    if Config.AI_ENABLED and not present('deepface'):
        print('\nFace search is not ready. Run: pip install -r requirements-ai.txt')
        raise SystemExit(2)
