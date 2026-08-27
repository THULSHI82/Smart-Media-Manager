import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db import execute, fetch_all, utc_now
from services.storage_service import delete_asset


def cleanup():
    now = utc_now()
    expired_embeddings = execute(
        'DELETE FROM face_embeddings WHERE is_claimed=0 AND expires_at IS NOT NULL AND expires_at < ?',
        (now,),
    )

    expired_images = fetch_all('''SELECT i.id, i.storage_public_id FROM images i
        JOIN events e ON e.id=i.event_id
        WHERE datetime(i.created_at, '+' || e.retention_days || ' days') < datetime(?)''', (now,))
    # The SQLite date expression above is intended for local mode. In Supabase,
    # use a scheduled SQL function or Edge Function for media retention.
    deleted_images = 0
    for image in expired_images:
        if delete_asset(image['storage_public_id']):
            execute('DELETE FROM images WHERE id=?', (image['id'],))
            deleted_images += 1
    print({'expired_embeddings_deleted': expired_embeddings, 'expired_images_deleted': deleted_images})


if __name__ == '__main__':
    cleanup()
