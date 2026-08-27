from flask import Blueprint, request
from db import fetch_all, fetch_one, update, utc_now
from services.privacy_service import purge_expired_unclaimed_embeddings
from utils.helpers import error, success
from utils.middleware import administrator_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.get('/summary')
@administrator_required
def summary():
    stats = fetch_one('''SELECT
        (SELECT COUNT(*) FROM users) AS users,
        (SELECT COUNT(*) FROM events) AS events,
        (SELECT COUNT(*) FROM images) AS images,
        (SELECT COUNT(*) FROM processing_jobs WHERE status='failed') AS failed_jobs,
        (SELECT COUNT(*) FROM deletion_requests WHERE status='pending') AS deletion_requests,
        (SELECT COUNT(*) FROM download_history) AS downloads''')
    activity = fetch_all('''SELECT a.*, u.name AS user_name FROM activity_logs a
                            LEFT JOIN users u ON u.id=a.user_id ORDER BY a.created_at DESC LIMIT 30''')
    return success({'stats': stats, 'activity': activity})


@admin_bp.get('/users')
@administrator_required
def users():
    return success({'users': fetch_all('SELECT id,name,email,role,is_active,created_at FROM users ORDER BY created_at DESC')})


@admin_bp.get('/deletion-requests')
@administrator_required
def deletion_requests():
    items = fetch_all('SELECT * FROM deletion_requests ORDER BY created_at DESC')
    return success({'deletion_requests': items})


@admin_bp.put('/deletion-requests/<request_id>')
@administrator_required
def resolve_deletion_request(request_id):
    item = fetch_one('SELECT * FROM deletion_requests WHERE id=?', (request_id,))
    if not item:
        return error('Deletion request not found.', 404)
    data = request.get_json(silent=True) or {}
    status = str(data.get('status') or '').strip().lower()
    if status not in ('pending', 'resolved', 'rejected'):
        return error('Status must be pending, resolved or rejected.')
    update('deletion_requests', request_id, {
        'status': status,
        'resolved_at': utc_now() if status in ('resolved', 'rejected') else None,
    })
    return success({'request': fetch_one('SELECT * FROM deletion_requests WHERE id=?', (request_id,))}, 'Deletion request updated.')


@admin_bp.post('/privacy/purge-expired-embeddings')
@administrator_required
def purge_embeddings():
    deleted = purge_expired_unclaimed_embeddings()
    return success({'deleted_embeddings': deleted}, 'Expired unclaimed face embeddings were purged.')
