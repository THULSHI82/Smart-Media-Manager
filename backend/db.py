import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from config import Config


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


def _sqlite_row_factory(cursor: sqlite3.Cursor, row: tuple) -> dict[str, Any]:
    return {description[0]: row[index] for index, description in enumerate(cursor.description)}


def _is_postgres() -> bool:
    return Config.DATA_BACKEND == 'supabase' and bool(Config.SUPABASE_DB_URL)


def _translate_query(query: str) -> str:
    return query.replace('?', '%s') if _is_postgres() else query


@contextmanager
def connection():
    if _is_postgres():
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError('Install psycopg[binary] to use the Supabase PostgreSQL backend.') from exc
        conn = psycopg.connect(Config.SUPABASE_DB_URL, row_factory=dict_row)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
        return

    path = Path(Config.DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = _sqlite_row_factory
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    if _is_postgres():
        # Run supabase/schema.sql once in the Supabase SQL editor before starting.
        for name, description in [
            ('Stage', 'Stage and presentation photographs'),
            ('Crowd', 'Large audience or crowd photographs'),
            ('Group', 'Group photographs containing multiple people'),
            ('Portrait', 'Single-person or close portrait photographs'),
            ('Sports', 'Sports and physical activity photographs'),
            ('General', 'Other event photographs'),
        ]:
            with connection() as conn:
                conn.execute(
                    'INSERT INTO categories (id, name, description, created_at) VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING',
                    (new_id(), name, description, utc_now()),
                )
        return

    schema_path = Path(__file__).resolve().parent / 'schema.sql'
    with connection() as conn:
        conn.executescript(schema_path.read_text(encoding='utf-8'))
        # Upgrade local development databases created by earlier project versions.
        existing = {row['name'] for row in conn.execute('PRAGMA table_info(images)').fetchall()}
        for column, ddl in {
            'original_file_size': 'INTEGER',
            'preprocessing_ms': 'REAL',
            'storage_saving_percent': 'REAL',
            'processing_ms': 'REAL',
        }.items():
            if column not in existing:
                conn.execute(f'ALTER TABLE images ADD COLUMN {column} {ddl}')
        job_existing = {row['name'] for row in conn.execute('PRAGMA table_info(processing_jobs)').fetchall()}
        if 'duration_ms' not in job_existing:
            conn.execute('ALTER TABLE processing_jobs ADD COLUMN duration_ms REAL')

        for name, description in [
            ('Stage', 'Stage and presentation photographs'),
            ('Crowd', 'Large audience or crowd photographs'),
            ('Group', 'Group photographs containing multiple people'),
            ('Portrait', 'Single-person or close portrait photographs'),
            ('Sports', 'Sports and physical activity photographs'),
            ('General', 'Other event photographs'),
        ]:
            conn.execute(
                'INSERT OR IGNORE INTO categories (id, name, description, created_at) VALUES (?, ?, ?, ?)',
                (new_id(), name, description, utc_now()),
            )


def fetch_one(query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    with connection() as conn:
        cursor = conn.execute(_translate_query(query), tuple(params))
        return cursor.fetchone()


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.execute(_translate_query(query), tuple(params))
        return list(cursor.fetchall())


def execute(query: str, params: Iterable[Any] = ()) -> int:
    with connection() as conn:
        cursor = conn.execute(_translate_query(query), tuple(params))
        return cursor.rowcount


def _adapt_value(value: Any) -> Any:
    return json.dumps(value) if isinstance(value, (dict, list)) else value


def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    columns = ', '.join(data.keys())
    values = [_adapt_value(v) for v in data.values()]
    if _is_postgres():
        placeholders = []
        for key in data:
            placeholders.append('%s::vector' if table == 'face_embeddings' and key == 'embedding' else '%s')
    else:
        placeholders = ['?'] * len(data)
    with connection() as conn:
        conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({', '.join(placeholders)})", values)
    return data


def update(table: str, record_id: str, data: dict[str, Any], id_column: str = 'id') -> None:
    marker = '%s' if _is_postgres() else '?'
    assignments = ', '.join(f'{key} = {marker}' for key in data)
    values = [_adapt_value(v) for v in data.values()]
    values.append(record_id)
    execute(f'UPDATE {table} SET {assignments} WHERE {id_column} = {marker}', values)


def log_activity(user_id: str | None, action: str, entity_type: str, entity_id: str | None, details: dict | None = None) -> None:
    insert('activity_logs', {
        'id': new_id(),
        'user_id': user_id,
        'action': action,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'details_json': details or {},
        'created_at': utc_now(),
    })
