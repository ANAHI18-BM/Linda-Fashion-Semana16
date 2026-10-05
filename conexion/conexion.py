import os
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor

@contextmanager
def get_connection():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError('Configure DATABASE_URL en el archivo .env.')
    conn = psycopg2.connect(url, cursor_factory=RealDictCursor, connect_timeout=10)
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def query(sql, params=(), one=False):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                return cur.fetchone() if one else cur.fetchall()
            return cur.rowcount
