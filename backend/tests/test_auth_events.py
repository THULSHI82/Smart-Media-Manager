from werkzeug.security import generate_password_hash
from db import insert, new_id, utc_now


def register(client, email='photo@example.com', role='photographer'):
    return client.post('/api/auth/register', json={
        'name': 'Test User', 'email': email,
        'password': 'Password123', 'role': role,
    })


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


def create_event(client, token, title='University Function'):
    return client.post('/api/events', headers=auth_header(token), json={
        'title': title, 'location': 'Colombo', 'retention_days': 30,
    })


def test_health_reports_runtime_and_ai_status(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'
    assert response.json['data_backend'] == 'sqlite'
    assert response.json['storage_backend'] == 'local'
    assert 'face_ai' in response.json
    assert 'classification' in response.json


def test_register_login_and_create_event(client):
    registration = register(client)
    assert registration.status_code == 201

    login = client.post('/api/auth/login', json={'email': 'photo@example.com', 'password': 'Password123'})
    assert login.status_code == 200
    assert login.json['user']['role'] == 'photographer'

    created = create_event(client, login.json['token'])
    assert created.status_code == 201
    assert len(created.json['event']['access_code']) == 8


def test_invalid_login_is_rejected(client):
    register(client)
    response = client.post('/api/auth/login', json={'email': 'photo@example.com', 'password': 'WrongPassword9'})
    assert response.status_code == 401


def test_participant_cannot_create_event(client):
    registration = register(client, 'participant@example.com', 'participant')
    token = registration.json['token']
    response = client.post('/api/events', headers=auth_header(token), json={'title': 'Blocked'})
    assert response.status_code == 403


def test_private_event_requires_access_code(client):
    token = register(client).json['token']
    created = create_event(client, token)
    event = created.json['event']

    blocked = client.get(f"/api/events/{event['id']}")
    assert blocked.status_code == 403

    allowed = client.get(f"/api/events/{event['id']}?access_code={event['access_code']}")
    assert allowed.status_code == 200
    assert allowed.json['event']['title'] == 'University Function'
    assert 'access_code' not in allowed.json['event']


def test_administrator_can_manage_photographer_event(client):
    photographer = register(client).json
    event = create_event(client, photographer['token']).json['event']

    insert('users', {
        'id': new_id(), 'name': 'Admin', 'email': 'admin-test@example.com',
        'password_hash': generate_password_hash('Admin1234'),
        'role': 'administrator', 'is_active': 1, 'created_at': utc_now(),
    })
    login = client.post('/api/auth/login', json={'email': 'admin-test@example.com', 'password': 'Admin1234'})
    assert login.status_code == 200
    token = login.json['token']

    qr = client.get(f"/api/events/{event['id']}/qr", headers=auth_header(token))
    assert qr.status_code == 200
    assert qr.json['access_code'] == event['access_code']

    processing = client.get(f"/api/processing/events/{event['id']}", headers=auth_header(token))
    assert processing.status_code == 200
