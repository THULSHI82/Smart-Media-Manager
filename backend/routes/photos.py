import logging
from pathlib import Path
from time import perf_counter

from flask import Blueprint, redirect, request, send_file
from werkzeug.utils import secure_filename

from config import Config
from db import execute, fetch_all, fetch_one, insert, log_activity, new_id, utc_now
from services.preprocessing_service import prepare_event_image
from services.storage_service import add_access_code, delete_asset, store_event_image
from tasks import dispatch_image_processing
from utils.helpers import allowed_file, error, success
from utils.middleware import current_role, current_user_id, photographer_required

photos_bp = Blueprint('photos', __name__)
logger = logging.getLogger(__name__)


def _manageable_event(event_id: str):
    if current_role() == 'administrator':
        return fetch_one('SELECT * FROM events WHERE id=?', (event_id,))
    return fetch_one('SELECT * FROM events WHERE id=? AND photographer_id=?', (event_id, current_user_id()))


def _secure_photo_urls(photo: dict, access_code: str | None) -> dict:
    output = dict(photo)
    output['image_url'] = add_access_code(output.get('image_url'), access_code)
    output['thumbnail_url'] = add_access_code(output.get('thumbnail_url'), access_code)
    return output


@photos_bp.post('/upload')
@photographer_required
def upload_photos():
    event_id = request.form.get('event_id', '').strip()
    event = _manageable_event(event_id) if event_id else None
    if not event:
        return error('A valid event manageable by this account is required.', 403)

    files = request.files.getlist('photos')
    if not files:
        return error('Select one or more photographs.')

    accepted, rejected = [], []
    for upload in files:
        filename = secure_filename(upload.filename or '')
        if not filename or not allowed_file(filename):
            rejected.append({'filename': upload.filename, 'reason': 'Unsupported file type.'})
            continue
        started = perf_counter()
        try:
            raw = upload.read()
            if not raw:
                raise ValueError('Empty upload.')
            prepared = prepare_event_image(raw)
            preprocessing_ms = round((perf_counter() - started) * 1000, 2)
            original_size = len(raw)
            optimized_size = len(prepared.optimized_bytes)
            saving = round(max(0.0, (1 - (optimized_size / max(original_size, 1))) * 100), 2)

            image_id = new_id()
            stored = store_event_image(event_id, image_id, prepared.optimized_bytes, prepared.thumbnail_bytes)
            now = utc_now()
            insert('images', {
                'id': image_id,
                'event_id': event_id,
                'photographer_id': event['photographer_id'],
                'category_id': None,
                'original_filename': filename,
                'storage_public_id': stored['public_id'],
                'image_url': stored['url'],
                'thumbnail_url': stored['thumbnail_url'],
                'width': prepared.width,
                'height': prepared.height,
                'file_size': optimized_size,
                'original_file_size': original_size,
                'preprocessing_ms': preprocessing_ms,
                'storage_saving_percent': saving,
                'processing_ms': None,
                'perceptual_hash': None,
                'blur_score': None,
                'is_blurry': 0,
                'is_duplicate': 0,
                'duplicate_of_id': None,
                'classification_label': None,
                'classification_confidence': None,
                'processing_status': 'queued',
                'processing_error': None,
                'created_at': now,
                'updated_at': now,
            })
            job = dispatch_image_processing(image_id, event_id)
            accepted.append({
                'image_id': image_id,
                'filename': filename,
                'thumbnail_url': add_access_code(stored['thumbnail_url'], event['access_code']),
                'job_id': job['job_id'],
                'processing_mode': job['mode'],
                'original_bytes': original_size,
                'optimized_bytes': optimized_size,
                'storage_saving_percent': saving,
                'preprocessing_ms': preprocessing_ms,
            })
        except (ValueError, OSError):
            rejected.append({'filename': filename, 'reason': 'The file is empty, corrupt or not a supported image.'})
        except Exception:
            logger.exception('Photo upload failed for %s', filename)
            rejected.append({'filename': filename, 'reason': 'The image could not be stored or processed.'})

    total_original = sum(item['original_bytes'] for item in accepted)
    total_optimized = sum(item['optimized_bytes'] for item in accepted)
    overall_saving = round(max(0.0, (1 - total_optimized / max(total_original, 1)) * 100), 2) if accepted else 0.0
    avg_preprocessing = round(sum(item['preprocessing_ms'] for item in accepted) / len(accepted), 2) if accepted else 0.0

    log_activity(current_user_id(), 'upload_batch', 'event', event_id, {
        'accepted': len(accepted), 'rejected': len(rejected),
        'original_bytes': total_original, 'optimized_bytes': total_optimized,
        'storage_saving_percent': overall_saving,
    })
    return success({
        'accepted': accepted,
        'rejected': rejected,
        'summary': {
            'accepted': len(accepted), 'rejected': len(rejected),
            'original_bytes': total_original, 'optimized_bytes': total_optimized,
            'storage_saving_percent': overall_saving,
            'average_preprocessing_ms': avg_preprocessing,
        },
    }, 'Upload accepted. Processing was dispatched to the configured worker or local background fallback.', 202)


@photos_bp.get('/event/<event_id>')
def event_photos(event_id):
    access_code = request.args.get('access_code', '').strip().upper()
    event = fetch_one('SELECT * FROM events WHERE id=?', (event_id,))
    if not event:
        return error('Event not found.', 404)
    if not event['is_public'] and access_code != event['access_code']:
        return error('A valid access code is required.', 403)
    include_flagged = request.args.get('include_flagged') == 'true'
    condition = '' if include_flagged else 'AND is_blurry=0 AND is_duplicate=0'
    photos = fetch_all(
        f'''SELECT id, image_url, thumbnail_url, original_filename, classification_label,
                   classification_confidence, blur_score, is_blurry, is_duplicate,
                   processing_status, processing_ms, storage_saving_percent, created_at
            FROM images WHERE event_id=? {condition} ORDER BY created_at DESC''',
        (event_id,),
    )
    code_for_media = event['access_code'] if not event['is_public'] else None
    return success({'photos': [_secure_photo_urls(photo, code_for_media) for photo in photos]})


@photos_bp.get('/manage/<event_id>')
@photographer_required
def manage_photos(event_id):
    event = _manageable_event(event_id)
    if not event:
        return error('Event not found or not manageable by this account.', 404)
    photos = fetch_all('SELECT * FROM images WHERE event_id=? ORDER BY created_at DESC', (event_id,))
    code_for_media = event['access_code'] if not event['is_public'] else None
    return success({'photos': [_secure_photo_urls(photo, code_for_media) for photo in photos]})


@photos_bp.delete('/<image_id>')
@photographer_required
def delete_photo(image_id):
    image = fetch_one('SELECT * FROM images WHERE id=?', (image_id,))
    if not image:
        return error('Image not found.', 404)
    event = _manageable_event(image['event_id'])
    if not event:
        return error('Image not found or not manageable by this account.', 404)
    delete_asset(image['storage_public_id'])
    execute('DELETE FROM images WHERE id=?', (image_id,))
    log_activity(current_user_id(), 'delete', 'image', image_id)
    return success(message='Image deleted.')


@photos_bp.get('/<image_id>/download')
def download_photo(image_id):
    access_code = request.args.get('access_code', '').strip().upper()
    image = fetch_one('''SELECT i.*, e.access_code, e.is_public FROM images i
                         JOIN events e ON e.id=i.event_id WHERE i.id=?''', (image_id,))
    if not image:
        return error('Image not found.', 404)
    if not image['is_public'] and access_code != image['access_code']:
        return error('A valid event access code is required.', 403)
    insert('download_history', {
        'id': new_id(),
        'user_id': None,
        'image_id': image_id,
        'event_id': image['event_id'],
        'requester_ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'created_at': utc_now(),
    })
    log_activity(None, 'download', 'image', image_id)
    if Config.STORAGE_BACKEND == 'local':
        path = Path(Config.LOCAL_UPLOAD_DIR) / image['storage_public_id']
        return send_file(path, as_attachment=True, download_name=image['original_filename'])
    return redirect(image['image_url'], code=302)
