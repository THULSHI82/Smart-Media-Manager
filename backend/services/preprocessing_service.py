import io
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageOps
import cv2
import numpy as np

from config import Config


@dataclass
class PreparedImage:
    original: Image.Image
    ai_image: Image.Image
    optimized_bytes: bytes
    thumbnail_bytes: bytes
    width: int
    height: int


def _resize_within(image: Image.Image, max_dimension: int) -> Image.Image:
    copy = image.copy()
    copy.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    return copy


def _clahe_rgb(image: Image.Image) -> Image.Image:
    array = np.array(image.convert('RGB'))
    lab = cv2.cvtColor(array, cv2.COLOR_RGB2LAB)
    light, a, b = cv2.split(lab)
    enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(light)
    result = cv2.merge((enhanced, a, b))
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_LAB2RGB))


def _jpeg_bytes(image: Image.Image, quality: int) -> bytes:
    output = io.BytesIO()
    image.convert('RGB').save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
    return output.getvalue()


def prepare_ai_image(image: Image.Image) -> Image.Image:
    """Create the normalised copy used by face extraction and classification.

    The stored/gallery image remains visually natural, while the AI copy receives a
    small contrast adjustment and CLAHE to reduce uneven illumination.
    """
    return _clahe_rgb(ImageEnhance.Contrast(image.convert('RGB')).enhance(1.03))


def prepare_event_image(raw_bytes: bytes) -> PreparedImage:
    image = Image.open(io.BytesIO(raw_bytes))
    image = ImageOps.exif_transpose(image).convert('RGB')
    image = _resize_within(image, Config.MAX_IMAGE_DIMENSION)

    ai_image = prepare_ai_image(image)
    thumbnail = _resize_within(image, Config.THUMBNAIL_DIMENSION)

    return PreparedImage(
        original=image,
        ai_image=ai_image,
        optimized_bytes=_jpeg_bytes(image, Config.JPEG_QUALITY),
        thumbnail_bytes=_jpeg_bytes(thumbnail, 78),
        width=image.width,
        height=image.height,
    )


def prepare_selfie(raw_bytes: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(raw_bytes))
    image = ImageOps.exif_transpose(image).convert('RGB')
    image = _resize_within(image, Config.SELFIE_MAX_DIMENSION)
    return prepare_ai_image(image)
