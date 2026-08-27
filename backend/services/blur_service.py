import cv2
import numpy as np
from PIL import Image
from config import Config


def laplacian_variance(image: Image.Image) -> float:
    rgb = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def analyse_blur(image: Image.Image, threshold: float | None = None) -> dict:
    value = laplacian_variance(image)
    limit = Config.BLUR_THRESHOLD if threshold is None else threshold
    return {'score': round(value, 3), 'is_blurry': value < limit, 'threshold': limit}
