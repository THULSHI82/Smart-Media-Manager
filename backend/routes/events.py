import base64
import io
from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required

from config import Config
from db import execute, fetch_all, fetch_one, insert, log_activity, new_id, update, utc_now
from utils.helpers import error, generate_access_code, success
from utils.middleware import current_role, current_user_id, photographer_required
from services.storage_service import delete_asset

events_bp = Blueprint('events', __name__)


def _manageable_event(event_id: str):
    if current_role() == 'administrator':
        return fetch_one('SELECT * FROM events WHERE id=?', (event_id,))
    return fetch_one('SELECT * FROM events WHERE id=? AND photographer_id=?', (event_id, current_user_id()))


@events_bp.post('')
@photographer_required
def create_event():
    data = request.get_json(silent=True) or {}
    title = str(data.get('title') or '').strip()
    if not title:
        return error('Event title is required.')
    try:
        retention_days = max(1, min(3650, int(data.get('retention_days') or 90)))
        embedding_days = max(1, min(3650, int(data.get('unclaimed_embedding_days') or 30)))
    except (TypeError, ValueError):
        return error('Retention values must be valid numbers.')

    code = generate_access_code()
    while fetch_one('SELECT id FROM events WHERE access_code=?', (code,)):
        code = generate_access_code()

    event_id = new_id()
    now = utc_now()
    event = {
        'id': event_id,
        'photographer_id': current_user_id(),
        'title': title,
        'description': str(data.get('description') or '').strip(),
        'event_date': data.get('event_date') or None,
        'location': str(data.get('location') or '').strip(),
        'access_code': code,
        'is_public': int(bool(data.get('is_public', False))),
        'retention_days': retention_days,
        'face_indexing_enabled': int(bool(data.get('face_indexing_enabled', True))),
        'unclaimed_embedding_days': embedding_days,
        'created_at': now,
        'updated_at': now,
    }
    insert('events', event)
    log_activity(current_user_id(), 'create', 'event', event_id)
    return success({'event': event}, 'Event created.', 201)


@events_bp.get('')
@jwt_required()
def list_events():
    user_id = current_user_id()
    role = get_jwt().get('role')
    if role == 'administrator':
        events = fetch_all('''SELECT e.*, u.name AS photographer_name,
                           (SELECT COUNT(*) FROM images i WHERE i.event_id=e.id) AS photo_count
                           FROM events e JOIN users u ON u.id=e.photographer_id ORDER BY e.created_at DESC''')
    else:
        events = fetch_all('''SELECT e.*,
                           (SELECT COUNT(*) FROM images i WHERE i.event_id=e.id) AS photo_count
                           FROM events e WHERE photographer_id=? ORDER BY created_at DESC''', (user_id,))
    return success({'events': events})


@events_bp.get('/<event_id>')
def event_details(event_id):
    code = request.args.get('access_code', '').strip().upper()
    event = fetch_one('''SELECT e.id, e.title, e.description, e.event_date, e.location,
                      e.access_code, e.is_public, e.created_at, u.name AS photographer_name,
                      (SELECT COUNT(*) FROM images i WHERE i.event_id=e.id AND i.processing_status='completed') AS photo_count
                      FROM events e JOIN users u ON u.id=e.photographer_id WHERE e.id=?''', (event_id,))
    if not event:
        return error('Event not found.', 404)
    if not event['is_public'] and code != event['access_code']:
        return error('A valid event access code is required.', 403)
    # Do not unnecessarily expose the private code in the public event-detail response.
    event.pop('access_code', None)
    return success({'event': event})


@events_bp.put('/<event_id>')
@photographer_required
def edit_event(event_id):
    event = _manageable_event(event_id)
    if not event:
        return error('Event not found or not manageable by this account.', 404)
    data = request.get_json(silent=True) or {}
    try:
        retention_days = max(1, min(3650, int(data.get('retention_days', event['retention_days']))))
        embedding_days = max(1, min(3650, int(data.get('unclaimed_embedding_days', event['unclaimed_embedding_days']))))
    except (TypeError, ValueError):
        return error('Retention values must be valid numbers.')
    values = {
        'title': str(data.get('title', event['title']) or '').strip(),
        'description': str(data.get('description', event['description'] or '') or '').strip(),
        'event_date': data.get('event_date', event['event_date']),
        'location': str(data.get('location', event['location'] or '') or '').strip(),
        'is_public': int(bool(data.get('is_public', event['is_public']))),
        'retention_days': retention_days,
        'face_indexing_enabled': int(bool(data.get('face_indexing_enabled', event['face_indexing_enabled']))),
        'unclaimed_embedding_days': embedding_days,
        'updated_at': utc_now(),
    }
    if not values['title']:
        return error('Event title is required.')
    update('events', event_id, values)
    log_activity(current_user_id(), 'update', 'event', event_id)
    return success({'event': fetch_one('SELECT * FROM events WHERE id=?', (event_id,))}, 'Event updated.')


@events_bp.delete('/<event_id>')
@photographer_required
def delete_event(event_id):
    event = _manageable_event(event_id)
    if not event:
        return error('Event not found or not manageable by this account.', 404)
    assets = fetch_all('SELECT storage_public_id FROM images WHERE event_id=?', (event_id,))
    for asset in assets:
        delete_asset(asset['storage_public_id'])
    execute('DELETE FROM events WHERE id=?', (event_id,))
    log_activity(current_user_id(), 'delete', 'event', event_id, {'media_assets': len(assets)})
    return success(message='Event, database records and associated media assets were deleted.')


@events_bp.get('/<event_id>/qr')
@photographer_required
def event_qr(event_id):
    event = _manageable_event(event_id)
    if not event:
        return error('Event not found or not manageable by this account.', 404)
    access_url = f"{Config.FRONTEND_URL.rstrip('/')}/search?event={event_id}&code={event['access_code']}"
    try:
        import qrcode
        image = qrcode.make(access_url)
        output = io.BytesIO()
        image.save(output, format='PNG')
        data_url = 'data:image/png;base64,' + base64.b64encode(output.getvalue()).decode('ascii')
    except Exception:
        data_url = None
    return success({'access_url': access_url, 'access_code': event['access_code'], 'qr_data_url': data_url})
