import traceback
from threading import Thread
from datetime import datetime, timedelta, timezone
from time import perf_counter

from config import Config
from db import execute, fetch_all, fetch_one, insert, log_activity, new_id, update, utc_now
from services.blur_service import analyse_blur
from services.classification_service import classify_image
from services.duplicate_service import closest_duplicate, compute_phash
from services.face_service import FaceProcessingError, FaceServiceUnavailable, extract_embeddings
from services.media_loader import load_pil
from services.preprocessing_service import prepare_ai_image


def _job_update(job_id: str, **values) -> None:
    update('processing_jobs', job_id, values)


def process_image(image_id: str, job_id: str) -> dict:
    clock = perf_counter()
    image_row = fetch_one('SELECT * FROM images WHERE id=?', (image_id,))
    if not image_row:
        _job_update(job_id, status='failed', error='Image record not found.', completed_at=utc_now(), duration_ms=0)
        return {'status': 'failed', 'error': 'Image record not found.'}

    _job_update(job_id, status='processing', progress=5, started_at=utc_now(), message='Loading optimised image')
    update('images', image_id, {'processing_status': 'processing', 'updated_at': utc_now()})

    try:
        image = load_pil(image_row['image_url'], image_row['storage_public_id'])
        ai_image = prepare_ai_image(image)

        _job_update(job_id, progress=20, message='Checking image sharpness')
        blur = analyse_blur(image)

        _job_update(job_id, progress=35, message='Checking exact and near duplicates')
        phash = compute_phash(image)
        known = fetch_all(
            'SELECT id, perceptual_hash FROM images WHERE event_id=? AND id<>? AND perceptual_hash IS NOT NULL',
            (image_row['event_id'], image_id),
        )
        duplicate = closest_duplicate(phash, known)

        _job_update(job_id, progress=55, message='Detecting and aligning faces')
        event = fetch_one('SELECT face_indexing_enabled, unclaimed_embedding_days FROM events WHERE id=?', (image_row['event_id'],))
        faces = []
        face_status = 'disabled'
        if event and event['face_indexing_enabled']:
            try:
                faces = extract_embeddings(ai_image)
                face_status = 'completed'
            except FaceServiceUnavailable:
                face_status = 'unavailable'
            except FaceProcessingError:
                face_status = 'error'

        expires_at = (datetime.now(timezone.utc) + timedelta(days=int(event['unclaimed_embedding_days'] if event else 30))).isoformat()
        execute('DELETE FROM face_embeddings WHERE image_id=?', (image_id,))
        for face in faces:
            insert('face_embeddings', {
                'id': new_id(),
                'image_id': image_id,
                'event_id': image_row['event_id'],
                'face_index': face['face_index'],
                'model_name': Config.FACE_MODEL,
                'embedding_json': face['embedding'],
                'embedding': face['embedding'],
                'detector_confidence': face['confidence'],
                'bounding_box_json': face['box'],
                'is_claimed': 0,
                'expires_at': expires_at,
                'created_at': utc_now(),
            })

        _job_update(job_id, progress=78, message='Classifying event photograph')
        classification = classify_image(ai_image, len(faces))
        category = fetch_one('SELECT id FROM categories WHERE name=?', (classification['label'],))
        duration_ms = round((perf_counter() - clock) * 1000, 2)

        update('images', image_id, {
            'category_id': category['id'] if category else None,
            'perceptual_hash': phash,
            'blur_score': blur['score'],
            'is_blurry': int(blur['is_blurry']),
            'is_duplicate': int(duplicate is not None),
            'duplicate_of_id': duplicate['image_id'] if duplicate else None,
            'classification_label': classification['label'],
            'classification_confidence': classification['confidence'],
            'processing_ms': duration_ms,
            'processing_status': 'completed',
            'processing_error': None,
            'updated_at': utc_now(),
        })
        message = f"Completed: {len(faces)} face(s), {classification['label']} category"
        if face_status == 'unavailable':
            message += '; face model unavailable in this runtime'
        elif face_status == 'error':
            message += '; face analysis skipped after backend error'
        elif not faces and face_status == 'completed':
            message += '; no detectable face'
        _job_update(job_id, status='completed', progress=100, message=message, completed_at=utc_now(), error=None, duration_ms=duration_ms)
        log_activity(image_row['photographer_id'], 'process', 'image', image_id, {
            'faces': len(faces), 'face_status': face_status, 'blurry': blur['is_blurry'],
            'duplicate': bool(duplicate), 'processing_ms': duration_ms,
            'classification_backend': classification.get('backend'),
        })
        return {
            'status': 'completed', 'image_id': image_id, 'faces': len(faces),
            'face_status': face_status, 'processing_ms': duration_ms,
            'classification_backend': classification.get('backend'),
        }
    except Exception as exc:
        duration_ms = round((perf_counter() - clock) * 1000, 2)
        message = str(exc)
        update('images', image_id, {
            'processing_status': 'failed',
            'processing_error': message,
            'processing_ms': duration_ms,
            'updated_at': utc_now(),
        })
        _job_update(job_id, status='failed', progress=100, error=message, message='Processing failed', completed_at=utc_now(), duration_ms=duration_ms)
        return {'status': 'failed', 'error': message, 'trace': traceback.format_exc(limit=3), 'processing_ms': duration_ms}


def dispatch_image_processing(image_id: str, event_id: str) -> dict:
    job_id = new_id()
    insert('processing_jobs', {
        'id': job_id,
        'event_id': event_id,
        'image_id': image_id,
        'task_id': None,
        'job_type': 'image_pipeline',
        'status': 'queued',
        'progress': 0,
        'message': 'Queued for background processing',
        'error': None,
        'started_at': None,
        'completed_at': None,
        'duration_ms': None,
        'created_at': utc_now(),
    })

    if Config.PROCESSING_SYNC:
        process_image(image_id, job_id)
        return {'job_id': job_id, 'task_id': None, 'mode': 'synchronous-local'}

    if Config.USE_CELERY:
        try:
            from celery_app import celery
            result = celery.send_task('tasks.process_image_task', args=[image_id, job_id])
            update('processing_jobs', job_id, {'task_id': result.id})
            return {'job_id': job_id, 'task_id': result.id, 'mode': 'celery'}
        except Exception as exc:
            update('processing_jobs', job_id, {'message': f'Queue unavailable; local fallback used: {exc}'})

    thread = Thread(target=process_image, args=(image_id, job_id), daemon=True)
    thread.start()
    return {'job_id': job_id, 'task_id': None, 'mode': 'threaded-local'}
