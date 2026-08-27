from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from db import fetch_one, insert, log_activity, new_id, utc_now
from utils.helpers import error, success, validate_email, validate_password

auth_bp = Blueprint('auth', __name__)


def _token_for(user: dict) -> str:
    return create_access_token(
        identity=user['id'],
        additional_claims={'role': user['role'], 'email': user['email'], 'name': user['name']},
    )


def _supabase_client():
    from supabase import create_client
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)


@auth_bp.post('/register')
def register():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'participant')

    if not name or not email or not password:
        return error('Name, email and password are required.')
    if not validate_email(email):
        return error('Enter a valid email address.')
    valid, reason = validate_password(password)
    if not valid:
        return error(reason)
    if role not in ('photographer', 'participant'):
        return error('Role must be photographer or participant.')
    if fetch_one('SELECT id FROM users WHERE email = ?', (email,)):
        return error('An account already exists for this email.', 409)

    try:
        if Config.AUTH_BACKEND == 'supabase':
            response = _supabase_client().auth.sign_up({'email': email, 'password': password})
            if not response.user:
                return error('Supabase did not create the account.', 400)
            user_id = str(response.user.id)
            password_hash = None
        else:
            user_id = new_id()
            password_hash = generate_password_hash(password)

        user = {
            'id': user_id,
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'is_active': 1,
            'created_at': utc_now(),
        }
        insert('users', user)
        token = _token_for(user)
        log_activity(user_id, 'register', 'user', user_id)
        return success({'token': token, 'user': {k: user[k] for k in ('id', 'name', 'email', 'role')}}, 'Registration successful.', 201)
    except Exception:
        return error('Registration could not be completed. Check the configured authentication backend.', 400)


@auth_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    user = fetch_one('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
    if not user:
        return error('Invalid email or password.', 401)

    try:
        if Config.AUTH_BACKEND == 'supabase':
            response = _supabase_client().auth.sign_in_with_password({'email': email, 'password': password})
            if not response.user or str(response.user.id) != str(user['id']):
                return error('Invalid email or password.', 401)
        elif not user.get('password_hash') or not check_password_hash(user['password_hash'], password):
            return error('Invalid email or password.', 401)
    except Exception:
        return error('Invalid email or password.', 401)

    token = _token_for(user)
    log_activity(user['id'], 'login', 'user', user['id'])
    return success({'token': token, 'user': {k: user[k] for k in ('id', 'name', 'email', 'role')}}, 'Login successful.')


@auth_bp.get('/me')
@jwt_required()
def me():
    user = fetch_one('SELECT id, name, email, role, created_at FROM users WHERE id = ?', (get_jwt_identity(),))
    if not user:
        return error('User not found.', 404)
    return success({'user': user})
