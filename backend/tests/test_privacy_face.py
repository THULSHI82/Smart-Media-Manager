import io
from PIL import Image


def sample_selfie():
    output = io.BytesIO()
    Image.new('RGB', (256, 256), 'white').save(output, format='JPEG')
    return output.getvalue()


def create_private_event(client):
    registration = client.post('/api/auth/register', json={
        'name': 'Photo', 'email': 'privacy-photo@example.com',
        'password': 'Password123', 'role': 'photographer',
    }).json
    event = client.post('/api/events', headers={'Authorization': f"Bearer {registration['token']}"}, json={'title': 'Private Event'}).json['event']
    return event


def test_privacy_deletion_request(client):
    response = client.post('/api/privacy/deletion-request', json={
        'email': 'participant@example.com', 'reason': 'Remove my event data',
    })
    assert response.status_code == 201
    assert response.json['request_id']


def test_selfie_search_requires_consent(client):
    event = create_private_event(client)
    response = client.post(f"/api/face/search/{event['id']}", data={
        'access_code': event['access_code'],
        'selfie': (io.BytesIO(sample_selfie()), 'selfie.jpg'),
    }, content_type='multipart/form-data')
    assert response.status_code == 422


def test_selfie_search_reports_ai_unavailable_instead_of_false_no_face(client):
    event = create_private_event(client)
    response = client.post(f"/api/face/search/{event['id']}", data={
        'access_code': event['access_code'],
        'consent': 'true',
        'selfie': (io.BytesIO(sample_selfie()), 'selfie.jpg'),
    }, content_type='multipart/form-data')
    assert response.status_code == 503
    assert 'disabled' in response.json['error'].lower() or 'deepface' in response.json['error'].lower()
