# db.py — PostgreSQL / psycopg2 database layer

import psycopg2
import psycopg2.extras
from datetime import datetime
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

_conn = None


def get_connection():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
    return _conn


def init_db():
    """Create tables if they don't exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS players (
        id       SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_sessions (
        id            SERIAL PRIMARY KEY,
        player_id     INTEGER REFERENCES players(id),
        score         INTEGER   NOT NULL,
        level_reached INTEGER   NOT NULL,
        played_at     TIMESTAMP DEFAULT NOW()
    );
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        return False


def get_or_create_player(username: str) -> int | None:
    """Return player id, creating the row if it doesn't exist."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) "
                "ON CONFLICT (username) DO NOTHING",
                (username,),
            )
            conn.commit()
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return None


def save_session(player_id: int, score: int, level: int):
    """Persist a finished game session."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) "
                "VALUES (%s, %s, %s)",
                (player_id, score, level),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] save_session error: {e}")
        return False


def get_personal_best(player_id: int) -> int:
    """Return the player's all-time highest score (0 if none)."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                (player_id,),
            )
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0


def get_leaderboard(limit: int = 10) -> list[dict]:
    """Return top <limit> scores across all players."""
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT p.username, gs.score, gs.level_reached,
                       gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC, gs.played_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []


def close():
    global _conn
    if _conn and not _conn.closed:
        _conn.close()
        _conn = None