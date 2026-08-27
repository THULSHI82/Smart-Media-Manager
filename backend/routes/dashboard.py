from flask import Blueprint
from db import fetch_all, fetch_one
from utils.helpers import success
from utils.middleware import current_user_id, photographer_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.get('/summary')
@photographer_required
def summary():
    user_id = current_user_id()
    stats = fetch_one('''SELECT
      (SELECT COUNT(*) FROM events WHERE photographer_id=?) AS events,
      (SELECT COUNT(*) FROM images WHERE photographer_id=?) AS photos,
      (SELECT COUNT(*) FROM images WHERE photographer_id=? AND is_blurry=1) AS blurry,
      (SELECT COUNT(*) FROM images WHERE photographer_id=? AND is_duplicate=1) AS duplicates,
      (SELECT COUNT(*) FROM images WHERE photographer_id=? AND processing_status IN ('queued','processing')) AS processing,
      (SELECT COALESCE(SUM(file_size),0) FROM images WHERE photographer_id=?) AS storage_bytes,
      (SELECT COALESCE(SUM(original_file_size),0) FROM images WHERE photographer_id=?) AS original_storage_bytes,
      (SELECT ROUND(AVG(preprocessing_ms),2) FROM images WHERE photographer_id=?) AS avg_preprocessing_ms,
      (SELECT ROUND(AVG(processing_ms),2) FROM images WHERE photographer_id=? AND processing_status='completed') AS avg_processing_ms''',
      (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
    original = float(stats.get('original_storage_bytes') or 0)
    optimised = float(stats.get('storage_bytes') or 0)
    stats['storage_saving_percent'] = round(max(0.0, (1 - optimised / original) * 100), 2) if original else 0.0

    recent_events = fetch_all('''SELECT e.*,
        (SELECT COUNT(*) FROM images i WHERE i.event_id=e.id) AS photo_count,
        (SELECT COUNT(*) FROM images i WHERE i.event_id=e.id AND i.processing_status='completed') AS completed_count
        FROM events e WHERE photographer_id=? ORDER BY created_at DESC LIMIT 5''', (user_id,))
    recent_jobs = fetch_all('''SELECT j.*, e.title AS event_title FROM processing_jobs j
        JOIN events e ON e.id=j.event_id WHERE e.photographer_id=? ORDER BY j.created_at DESC LIMIT 8''', (user_id,))
    return success({'stats': stats, 'recent_events': recent_events, 'recent_jobs': recent_jobs})
