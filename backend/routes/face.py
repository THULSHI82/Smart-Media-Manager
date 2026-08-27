import logging
from flask import Blueprint, request

from db import fetch_one, insert, log_activity, new_id, utc_now
from services.face_service import FaceProcessingError, FaceServiceUnavailable, extract_embeddings
from services.preprocessing_service import prepare_selfie
from services.storage_service import add_access_code
from services.vector_service import search_event_faces
from utils.helpers import error, success

face_bp = Blueprint('face', __name__)
logger = logging.getLogger(__name__)


@face_bp.post('/search/<event_id>')
def search_by_selfie(event_id):
    event = fetch_one('SELECT * FROM events WHERE id=?', (event_id,))
    if not event:
        return error('Event not found.', 404)

    access_code = (request.form.get('access_code') or '').strip().upper()
    if not event['is_public'] and access_code != event['access_code']:
        return error('A valid event access code is required.', 403)

    consent = (request.form.get('consent') or '').lower() in ('true', '1', 'yes')
    if not consent:
        return error('Biometric processing consent is required.', 422)
    selfie = request.files.get('selfie')
    if not selfie or not selfie.filename:
        return error('Select a clear selfie image.')

    insert('consents', {
        'id': new_id(),
        'event_id': event_id,
        'user_id': None,
        'consent_type': 'selfie_face_matching',
        'consent_version': '1.0',
        'accepted': 1,
        'requester_ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'created_at': utc_now(),
    })

    try:
        raw = selfie.read()
        if not raw:
            return error('The selfie file is empty.', 400)
        image = prepare_selfie(raw)
        faces = extract_embeddings(image)
        if len(faces) != 1:
            message = 'No face was detected.' if not faces else 'Please upload a selfie containing only one clear face.'
            return error(message, 422)

        matches = search_event_faces(event_id, faces[0]['embedding'])
        code_for_media = event['access_code'] if not event['is_public'] else None
        for item in matches:
            item['image_url'] = add_access_code(item.get('image_url'), code_for_media)
            item['thumbnail_url'] = add_access_code(item.get('thumbnail_url'), code_for_media)

        log_activity(None, 'selfie_search', 'event', event_id, {'matches': len(matches)})
        return success({
            'event': {'id': event['id'], 'title': event['title']},
            'matches': matches,
            'match_count': len(matches),
            'privacy_notice': 'The uploaded selfie is processed in memory and is not retained by this endpoint.',
        })
    except FaceServiceUnavailable as exc:
        return error(str(exc), 503)
    except FaceProcessingError:
        logger.exception('Face-search backend failed')
        return error('The face-search service could not process this image.', 500)
    except (OSError, ValueError):
        return error('The selfie is corrupt or not a supported image.', 400)
    except Exception:
        logger.exception('Unexpected selfie-search failure')
        return error('Selfie processing failed unexpectedly.', 500)
