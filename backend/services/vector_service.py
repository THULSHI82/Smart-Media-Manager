import json
from config import Config
from db import fetch_all
from services.face_service import match_embeddings


def search_event_faces(event_id: str, query_embedding: list[float], threshold: float | None = None, limit: int = 100) -> list[dict]:
    if Config.DATA_BACKEND == 'supabase' and Config.SUPABASE_URL and Config.SUPABASE_SERVICE_KEY:
        try:
            from supabase import create_client
            client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
            result = client.rpc('match_event_faces', {
                'query_embedding': query_embedding,
                'target_event_id': event_id,
                'match_threshold': threshold or Config.FACE_COSINE_THRESHOLD,
                'match_count': limit,
            }).execute()
            return result.data or []
        except Exception:
            pass

    rows = fetch_all(
        '''SELECT f.image_id, f.embedding_json, i.image_url, i.thumbnail_url,
                  i.original_filename, i.classification_label, i.is_blurry, i.is_duplicate
           FROM face_embeddings f
           JOIN images i ON i.id = f.image_id
           WHERE f.event_id = ? AND i.processing_status = 'completed'
             AND i.is_blurry = 0 AND i.is_duplicate = 0 ''',
        (event_id,),
    )
    prepared = []
    for row in rows:
        try:
            embedding = json.loads(row.pop('embedding_json'))
        except (TypeError, json.JSONDecodeError):
            continue
        prepared.append({**row, 'embedding': embedding})
    matches = match_embeddings(query_embedding, prepared, threshold)
    return [
        {
            'image_id': item['image_id'],
            'image_url': item['image_url'],
            'thumbnail_url': item.get('thumbnail_url'),
            'filename': item.get('original_filename'),
            'category': item.get('classification_label'),
            'similarity': round(float(item['similarity']), 4),
            'confidence_percent': round(float(item['similarity']) * 100, 2),
        }
        for item in matches[:limit]
    ]
