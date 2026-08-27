import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app


@pytest.fixture()
def app(tmp_path):
    app = create_app({
        'TESTING': True,
        'DATABASE_PATH': str(tmp_path / 'test.db'),
        'LOCAL_UPLOAD_DIR': str(tmp_path / 'uploads'),
        'API_BASE_URL': 'http://localhost:5001',
        'AI_ENABLED': False,
        'USE_CELERY': False,
        'PROCESSING_SYNC': True,
        'STORAGE_BACKEND': 'local',
        'DATA_BACKEND': 'sqlite',
        'AUTH_BACKEND': 'local',
    })
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
