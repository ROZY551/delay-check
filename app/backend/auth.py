"""회원가입·로그인·조회 기록 (SQLite 파일 하나).

비밀번호는 그대로 저장하지 않고 PBKDF2(SHA-256)로 해시해서 저장한다.
Streamlit Cloud에서는 앱이 재시작되면 이 파일이 초기화될 수 있다 (시연용으로는 충분).
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from backend.weather import KST

DB_PATH = Path(__file__).resolve().parent / "data" / "delaycheck.db"
HISTORY_LIMIT = 10
USERNAME_RE = re.compile(r"^[A-Za-z0-9]{4,12}$")


def now_kst() -> datetime:
    """서버가 UTC여도 한국 시간으로 저장 (조회 기록 화면에 그대로 나온다)."""
    return datetime.now(KST).replace(tzinfo=None)


def _connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def init_db(path: Path = DB_PATH) -> None:
    with _connect(path) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            pw_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            flight_no TEXT NOT NULL,
            airline TEXT, dest TEXT, dest_code TEXT,
            dep_at TEXT NOT NULL,
            prob REAL NOT NULL,
            level TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)


def _hash(pw: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 200_000).hex()


# ---------- 회원 ----------
def username_available(username: str, path: Path = DB_PATH) -> bool:
    with _connect(path) as con:
        return con.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone() is None


def validate_signup(name: str, username: str, pw: str, pw2: str, agreed: bool) -> str | None:
    """문제가 있으면 안내 문장, 없으면 None"""
    if not name.strip():
        return "이름(닉네임)을 입력해 주세요."
    if not USERNAME_RE.match(username):
        return "아이디는 영문·숫자 4~12자로 입력해 주세요."
    if len(pw) < 8:
        return "비밀번호는 8자 이상이어야 해요."
    if pw != pw2:
        return "비밀번호 확인이 일치하지 않아요."
    if not agreed:
        return "필수 항목에 동의해 주세요."
    return None


def create_user(name: str, username: str, pw: str, path: Path = DB_PATH) -> bool:
    if not username_available(username, path):
        return False
    salt = os.urandom(16)
    with _connect(path) as con:
        con.execute("INSERT INTO users (username, name, pw_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
                    (username, name.strip(), _hash(pw, salt), salt.hex(), now_kst().isoformat(timespec="seconds")))
    return True


def verify_user(username: str, pw: str, path: Path = DB_PATH) -> dict | None:
    with _connect(path) as con:
        r = con.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if r is None or not hmac.compare_digest(r["pw_hash"], _hash(pw, bytes.fromhex(r["salt"]))):
        return None
    return {"id": r["id"], "username": r["username"], "name": r["name"]}


# ---------- 조회 기록 ----------
def add_history(user_id: int, result: dict, path: Path = DB_PATH) -> None:
    f = result["flight"]
    with _connect(path) as con:
        con.execute("""INSERT INTO history (user_id, flight_no, airline, dest, dest_code, dep_at, prob, level, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, f["편명"], f["항공사"], f["도착지"], f["도착코드"],
                     result["dep"].isoformat(timespec="minutes"), result["prob"], result["level"],
                     now_kst().isoformat(timespec="minutes")))
        con.execute("""DELETE FROM history WHERE user_id = ? AND id NOT IN
                       (SELECT id FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?)""",
                    (user_id, user_id, HISTORY_LIMIT))


def list_history(user_id: int, path: Path = DB_PATH) -> list[dict]:
    with _connect(path) as con:
        rows = con.execute("SELECT * FROM history WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    return [dict(r) for r in rows]


def delete_history(user_id: int, history_id: int, path: Path = DB_PATH) -> None:
    with _connect(path) as con:
        con.execute("DELETE FROM history WHERE user_id = ? AND id = ?", (user_id, history_id))


def clear_history(user_id: int, path: Path = DB_PATH) -> None:
    with _connect(path) as con:
        con.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
