import sqlite3
import bcrypt
import os
from datetime import datetime
 
DB_PATH = "mindease.db"
 
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
 
def init_db():
    conn = get_connection()
    c = conn.cursor()
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            emotion TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS emotion_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            emotion TEXT NOT NULL,
            burnout_score REAL DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS strategy_selections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            strategy TEXT NOT NULL,
            emotion_context TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
 
    conn.commit()
    conn.close()
 
# ── User Auth ──────────────────────────────────────────────────────────────────
 
def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, pw_hash)
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists."
        return False, "Email already registered."
 
def verify_user(username: str, password: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return dict(row)
    return None
 
# ── Chat ───────────────────────────────────────────────────────────────────────
 
def save_message(user_id: int, role: str, content: str, emotion: str = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_messages (user_id, role, content, emotion) VALUES (?, ?, ?, ?)",
        (user_id, role, content, emotion)
    )
    conn.commit()
    conn.close()
 
def get_chat_history(user_id: int, limit: int = 50) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM chat_messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]
 
# ── Emotions ──────────────────────────────────────────────────────────────────
 
def log_emotion(user_id: int, emotion: str, burnout_score: float):
    conn = get_connection()
    conn.execute(
        "INSERT INTO emotion_logs (user_id, emotion, burnout_score) VALUES (?, ?, ?)",
        (user_id, emotion, burnout_score)
    )
    conn.commit()
    conn.close()
 
def get_emotion_history(user_id: int, days: int = 7) -> list:
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM emotion_logs WHERE user_id = ?
           AND timestamp >= datetime('now', ?)
           ORDER BY timestamp ASC""",
        (user_id, f"-{days} days")
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
# ── Strategies ────────────────────────────────────────────────────────────────
 
def save_strategy(user_id: int, strategy: str, emotion_context: str = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO strategy_selections (user_id, strategy, emotion_context) VALUES (?, ?, ?)",
        (user_id, strategy, emotion_context)
    )
    conn.commit()
    conn.close()
 
def get_preferred_strategies(user_id: int) -> dict:
    conn = get_connection()
    rows = conn.execute(
        """SELECT strategy, COUNT(*) as cnt FROM strategy_selections
           WHERE user_id = ? GROUP BY strategy ORDER BY cnt DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return {r["strategy"]: r["cnt"] for r in rows}
 