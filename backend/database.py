# backend/database.py
# Persistance SQLite — utilisateurs et profils (vrai SaaS)

import sqlite3
import hashlib
import uuid
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "portfoliosense.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id        TEXT PRIMARY KEY,
            email     TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS profiles (
            user_id   TEXT PRIMARY KEY REFERENCES users(id),
            capital   REAL    DEFAULT 10000,
            horizon   INTEGER DEFAULT 5,
            perte_max INTEGER DEFAULT 15,
            profil    TEXT    DEFAULT 'equilibre',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token     TEXT PRIMARY KEY,
            user_id   TEXT REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(("portfoliosense_salt_" + password).encode()).hexdigest()


def create_user(email: str, password: str) -> str | None:
    conn = get_db()
    user_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO users (id, email, password) VALUES (?, ?, ?)",
            (user_id, email.lower().strip(), hash_password(password)),
        )
        conn.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None  # email déjà pris
    finally:
        conn.close()


def verify_user(email: str, password: str) -> str | None:
    conn = get_db()
    row = conn.execute(
        "SELECT id, password FROM users WHERE email = ?",
        (email.lower().strip(),),
    ).fetchone()
    conn.close()
    if row and row["password"] == hash_password(password):
        return row["id"]
    return None


def create_session(user_id: str) -> str:
    token = str(uuid.uuid4())
    conn = get_db()
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token


def get_user_from_token(token: str) -> str | None:
    conn = get_db()
    row = conn.execute(
        "SELECT user_id FROM sessions WHERE token = ?", (token,)
    ).fetchone()
    conn.close()
    return row["user_id"] if row else None


def get_profile(user_id: str) -> dict:
    conn = get_db()
    row = conn.execute(
        "SELECT capital, horizon, perte_max, profil FROM profiles WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else {}


def update_profile(user_id: str, capital: float, horizon: int,
                   perte_max: int, profil: str):
    conn = get_db()
    conn.execute(
        """UPDATE profiles
           SET capital = ?, horizon = ?, perte_max = ?, profil = ?,
               updated_at = CURRENT_TIMESTAMP
           WHERE user_id = ?""",
        (capital, horizon, perte_max, profil, user_id),
    )
    conn.commit()
    conn.close()
