import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from werkzeug.security import generate_password_hash
from db import fetch_one, init_db, insert, new_id, utc_now


def create_user(name: str, email: str, role: str, password: str):
    if fetch_one('SELECT id FROM users WHERE email=?', (email,)):
        print(f'Exists: {email}')
        return
    insert('users', {
        'id': new_id(), 'name': name, 'email': email,
        'password_hash': generate_password_hash(password),
        'role': role, 'is_active': 1, 'created_at': utc_now(),
    })
    print(f'Created: {email} ({role})')


if __name__ == '__main__':
    init_db()
    password = os.getenv('DEMO_PASSWORD', 'Demo1234')
    create_user('Demo Photographer', 'photographer@example.com', 'photographer', password)
    create_user('Demo Administrator', 'admin@example.com', 'administrator', password)
    print('Change the demo password before a public demonstration.')
