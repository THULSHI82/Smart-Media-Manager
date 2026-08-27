from flask import Blueprint, request
from db import insert, new_id, utc_now
from utils.helpers import error, success, validate_email

privacy_bp = Blueprint('privacy', __name__)


@privacy_bp.post('/deletion-request')
def deletion_request():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    if not validate_email(email):
        return error('Enter a valid email address.')
    request_id = new_id()
    insert('deletion_requests', {
        'id': request_id,
        'user_id': None,
        'email': email,
        'reason': data.get('reason', '').strip(),
        'status': 'pending',
        'created_at': utc_now(),
        'resolved_at': None,
    })
    return success({'request_id': request_id}, 'Deletion request recorded.', 201)


@privacy_bp.get('/policy')
def policy():
    return success({'policy': {
        'selfie_retention': 'Selfies submitted for search are processed in memory and are not stored by the search endpoint.',
        'embedding_purpose': 'Facial embeddings are restricted to authorised event-photo retrieval.',
        'consent': 'Explicit consent is required before biometric matching.',
        'access': 'Private events require an event-specific access code.',
        'deletion': 'Users can submit a deletion request for personal data and biometric records.',
    }})
