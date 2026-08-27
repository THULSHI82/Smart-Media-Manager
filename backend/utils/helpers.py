import re
import secrets
import string
from pathlib import Path
from flask import jsonify
from config import Config


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def safe_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip('.')
    return suffix if suffix in Config.ALLOWED_EXTENSIONS else 'jpg'


def validate_email(email: str) -> bool:
    return bool(re.match(r'^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$', email))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, 'Password must be at least 8 characters.'
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one letter and one number.'
    return True, ''


def generate_access_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def success(data: dict | None = None, message: str | None = None, code: int = 200):
    payload = {'success': True}
    if message:
        payload['message'] = message
    if data:
        payload.update(data)
    return jsonify(payload), code


def error(message: str, code: int = 400, details: dict | None = None):
    payload = {'success': False, 'error': message}
    if details:
        payload['details'] = details
    return jsonify(payload), code
