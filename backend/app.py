import importlib.util
import logging
from pathlib import Path

from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from db import fetch_one, init_db
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.events import events_bp
from routes.face import face_bp
from routes.photos import photos_bp
from routes.privacy import privacy_bp
from routes.processing import processing_bp
from services.privacy_service import purge_expired_unclaimed_embeddings
from utils.helpers import error

logger = logging.getLogger(__name__)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
        for key, value in test_config.items():
            if hasattr(Config, key):
                setattr(Config, key, value)

    CORS(app, resources={r'/api/*': {'origins': Config.CORS_ORIGINS}})
    JWTManager(app)
    init_db()
    try:
        purge_expired_unclaimed_embeddings()
    except Exception:
        logger.exception('Could not purge expired face embeddings during startup')

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(photos_bp, url_prefix='/api/photos')
    app.register_blueprint(face_bp, url_prefix='/api/face')
    app.register_blueprint(processing_bp, url_prefix='/api/processing')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(privacy_bp, url_prefix='/api/privacy')

    @app.get('/api/health')
    def health():
        deepface_available = importlib.util.find_spec('deepface') is not None
        tensorflow_available = importlib.util.find_spec('tensorflow') is not None
        model_path = Path(Config.CLASSIFICATION_MODEL_PATH) if Config.CLASSIFICATION_MODEL_PATH else None
        return {
            'status': 'ok',
            'service': 'Smart Media Manager API',
            'storage_backend': Config.STORAGE_BACKEND,
            'data_backend': Config.DATA_BACKEND,
            'background_mode': 'celery' if Config.USE_CELERY else ('synchronous' if Config.PROCESSING_SYNC else 'local fallback'),
            'face_ai': {
                'enabled': Config.AI_ENABLED,
                'deepface_available': deepface_available,
                'model': Config.FACE_MODEL,
                'detector': Config.FACE_DETECTOR,
            },
            'classification': {
                'configured_backend': Config.CLASSIFIER_BACKEND,
                'tensorflow_available': tensorflow_available,
                'trained_model_available': bool(model_path and model_path.exists()),
            },
        }, 200

    @app.get('/media/<path:filename>')
    def media(filename: str):
        """Serve local event media only after event-level access is validated."""
        parts = Path(filename).parts
        if len(parts) < 3 or parts[0] != 'events':
            return error('Media not found.', 404)
        event_id = parts[1]
        event = fetch_one('SELECT id, access_code, is_public FROM events WHERE id=?', (event_id,))
        if not event:
            return error('Media not found.', 404)
        access_code = (request.args.get('access_code') or '').strip().upper()
        if not event['is_public'] and access_code != event['access_code']:
            return error('A valid event access code is required.', 403)
        return send_from_directory(Path(Config.LOCAL_UPLOAD_DIR), filename)

    @app.errorhandler(413)
    def too_large(_):
        return {'success': False, 'error': 'The upload exceeds the configured size limit.'}, 413

    @app.errorhandler(500)
    def internal_error(exc):
        logger.exception('Unhandled API error', exc_info=exc)
        return {'success': False, 'error': 'An unexpected server error occurred.'}, 500

    return app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5001, debug=Config.DEBUG)
