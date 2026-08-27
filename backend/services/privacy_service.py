from datetime import datetime, timezone

from db import execute


def purge_expired_unclaimed_embeddings() -> int:
    """Delete temporary, unclaimed biometric vectors after their retention deadline."""
    now = datetime.now(timezone.utc).isoformat()
    return execute(
        'DELETE FROM face_embeddings WHERE is_claimed=0 AND expires_at IS NOT NULL AND expires_at < ?',
        (now,),
    )
