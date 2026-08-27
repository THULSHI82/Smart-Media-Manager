import os
import secrets
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


_RUNTIME_SECRET = os.getenv('SECRET_KEY') or secrets.token_urlsafe(48)


class Config:
    # When no .env is present, use an ephemeral high-entropy local secret rather than
    # a predictable hard-coded key. Production deployments should set both values.
    SECRET_KEY = _RUNTIME_SECRET
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or _RUNTIME_SECRET
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_HOURS', '24')))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_MB', '50')) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5001')

    DATA_BACKEND = os.getenv('DATA_BACKEND', 'sqlite').lower()
    AUTH_BACKEND = os.getenv('AUTH_BACKEND', 'local').lower()
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'smart_media.db'))

    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')

    STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'local').lower()
    LOCAL_UPLOAD_DIR = os.getenv('LOCAL_UPLOAD_DIR', str(BASE_DIR / 'uploads'))
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    USE_CELERY = os.getenv('USE_CELERY', 'false').lower() == 'true'
    CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'false').lower() == 'true'
    # Deterministic synchronous mode is intended for automated tests/benchmarks only.
    PROCESSING_SYNC = os.getenv('PROCESSING_SYNC', 'false').lower() == 'true'

    AI_ENABLED = os.getenv('AI_ENABLED', 'true').lower() == 'true'
    FACE_MODEL = os.getenv('FACE_MODEL', 'Facenet512')
    FACE_DETECTOR = os.getenv('FACE_DETECTOR', 'retinaface')
    FACE_COSINE_THRESHOLD = float(os.getenv('FACE_COSINE_THRESHOLD', '0.68'))
    BLUR_THRESHOLD = float(os.getenv('BLUR_THRESHOLD', '100'))
    DUPLICATE_HASH_DISTANCE = int(os.getenv('DUPLICATE_HASH_DISTANCE', '8'))
    CLASSIFIER_BACKEND = os.getenv('CLASSIFIER_BACKEND', 'heuristic').lower()
    CLASSIFICATION_MODEL_PATH = os.getenv('CLASSIFICATION_MODEL_PATH', '')

    MAX_IMAGE_DIMENSION = int(os.getenv('MAX_IMAGE_DIMENSION', '2048'))
    THUMBNAIL_DIMENSION = int(os.getenv('THUMBNAIL_DIMENSION', '480'))
    JPEG_QUALITY = int(os.getenv('JPEG_QUALITY', '85'))
    SELFIE_MAX_DIMENSION = int(os.getenv('SELFIE_MAX_DIMENSION', '1024'))
    EMBEDDING_RETENTION_DAYS = int(os.getenv('EMBEDDING_RETENTION_DAYS', '90'))

    CORS_ORIGINS = [x.strip() for x in os.getenv('CORS_ORIGINS', FRONTEND_URL).split(',') if x.strip()]
