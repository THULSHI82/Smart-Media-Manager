from flask import Blueprint
from db import fetch_all, fetch_one
from utils.helpers import error, success
from utils.middleware import current_role, current_user_id, photographer_required

processing_bp = Blueprint('processing', __name__)


def _manageable_event(event_id: str):
    if current_role() == 'administrator':
        return fetch_one('SELECT id FROM events WHERE id=?', (event_id,))
    return fetch_one('SELECT id FROM events WHERE id=? AND photographer_id=?', (event_id, current_user_id()))


@processing_bp.get('/jobs/<job_id>')
@photographer_required
def job_status(job_id):
    if current_role() == 'administrator':
        job = fetch_one('SELECT * FROM processing_jobs WHERE id=?', (job_id,))
    else:
        job = fetch_one('''SELECT j.* FROM processing_jobs j
                           JOIN events e ON e.id=j.event_id
                           WHERE j.id=? AND e.photographer_id=?''', (job_id, current_user_id()))
    if not job:
        return error('Processing job not found.', 404)
    return success({'job': job})


@processing_bp.get('/events/<event_id>')
@photographer_required
def event_processing(event_id):
    if not _manageable_event(event_id):
        return error('Event not found or not manageable by this account.', 404)
    jobs = fetch_all('SELECT * FROM processing_jobs WHERE event_id=? ORDER BY created_at DESC', (event_id,))
    counts = fetch_one('''SELECT COUNT(*) AS total,
                          SUM(CASE WHEN processing_status='completed' THEN 1 ELSE 0 END) AS completed,
                          SUM(CASE WHEN processing_status='failed' THEN 1 ELSE 0 END) AS failed,
                          SUM(CASE WHEN processing_status IN ('queued','processing') THEN 1 ELSE 0 END) AS pending,
                          ROUND(AVG(processing_ms),2) AS average_processing_ms
                          FROM images WHERE event_id=?''', (event_id,))
    return success({'jobs': jobs, 'counts': counts})
