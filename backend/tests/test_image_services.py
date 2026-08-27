import io
from urllib.parse import urlsplit
from PIL import Image, ImageDraw

from services.preprocessing_service import prepare_event_image
from services.blur_service import analyse_blur
from services.duplicate_service import compute_phash, closest_duplicate


def sample_bytes(width=1600, height=1000):
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    for x in range(0, width, 20):
        draw.line((x, 0, width - x, height), fill='black', width=2)
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=95)
    return output.getvalue()


def register_and_event(client):
    registration = client.post('/api/auth/register', json={
        'name': 'Photo', 'email': 'upload@example.com',
        'password': 'Password123', 'role': 'photographer',
    }).json
    token = registration['token']
    event = client.post('/api/events', headers={'Authorization': f'Bearer {token}'}, json={'title': 'Upload Test'}).json['event']
    return token, event


def upload_one(client, token, event_id, filename='photo.jpg', payload=None):
    payload = sample_bytes() if payload is None else payload
    return client.post('/api/photos/upload', headers={'Authorization': f'Bearer {token}'}, data={
        'event_id': event_id,
        'photos': (io.BytesIO(payload), filename),
    }, content_type='multipart/form-data')


def test_preprocessing_resizes_and_creates_thumbnail():
    prepared = prepare_event_image(sample_bytes(3200, 2000))
    assert max(prepared.width, prepared.height) <= 2048
    assert len(prepared.optimized_bytes) > 1000
    assert len(prepared.thumbnail_bytes) > 500
    assert prepared.ai_image.size == prepared.original.size


def test_blur_and_duplicate_services():
    prepared = prepare_event_image(sample_bytes())
    result = analyse_blur(prepared.original)
    assert result['score'] >= 0
    candidate = compute_phash(prepared.original)
    match = closest_duplicate(candidate, [{'id': 'same', 'perceptual_hash': candidate}])
    assert match['image_id'] == 'same'
    assert match['distance'] == 0


def test_upload_processing_and_measured_metrics(client):
    token, event = register_and_event(client)
    response = upload_one(client, token, event['id'])
    assert response.status_code == 202
    assert response.json['summary']['accepted'] == 1
    assert response.json['summary']['average_preprocessing_ms'] >= 0

    managed = client.get(f"/api/photos/manage/{event['id']}", headers={'Authorization': f'Bearer {token}'})
    assert managed.status_code == 200
    photo = managed.json['photos'][0]
    assert photo['processing_status'] == 'completed'
    assert photo['preprocessing_ms'] is not None
    assert photo['processing_ms'] is not None
    assert photo['original_file_size'] > 0
    assert photo['file_size'] > 0


def test_second_identical_upload_is_flagged_duplicate(client):
    token, event = register_and_event(client)
    payload = sample_bytes()
    assert upload_one(client, token, event['id'], 'first.jpg', payload).status_code == 202
    assert upload_one(client, token, event['id'], 'second.jpg', payload).status_code == 202

    managed = client.get(f"/api/photos/manage/{event['id']}", headers={'Authorization': f'Bearer {token}'})
    photos = managed.json['photos']
    duplicate_count = sum(int(item['is_duplicate']) for item in photos)
    assert duplicate_count == 1


def test_private_local_media_cannot_be_opened_without_event_code(client):
    token, event = register_and_event(client)
    upload_one(client, token, event['id'])
    managed = client.get(f"/api/photos/manage/{event['id']}", headers={'Authorization': f'Bearer {token}'})
    thumb_url = managed.json['photos'][0]['thumbnail_url']
    parsed = urlsplit(thumb_url)

    blocked = client.get(parsed.path)
    assert blocked.status_code == 403

    allowed = client.get(f'{parsed.path}?{parsed.query}')
    assert allowed.status_code == 200


def test_invalid_upload_is_rejected_without_crashing(client):
    token, event = register_and_event(client)
    response = upload_one(client, token, event['id'], 'notes.txt', b'not an image')
    assert response.status_code == 202
    assert response.json['summary']['accepted'] == 0
    assert response.json['summary']['rejected'] == 1
