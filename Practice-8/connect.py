import psycopg2
from config import db_config

def get_connection():
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        return None

def close_connection(conn):
    if conn:
        conn.close()

def execute_query(query, params=None):
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        close_connection(conn)

def fetch_data(query, params=None):
    conn = get_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        data = cur.fetchall()
        cur.close()
        return data
    except Exception as e:
        return None
    finally:
        close_connection(conn)

def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(20) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(query)

if __name__ == "__main__":
    create_table()
