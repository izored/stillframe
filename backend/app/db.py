"""SQLite persistence — local-first.

Schema carries the foundation repo's model (facts, mood, summaries) and adds
Stillframe's structure: scenes, frames, arcs. Encryption at rest (SQLCipher)
and per-scene passcodes arrive in a later security phase; the schema is shaped
for it now (scenes.private, scenes.encrypted).
"""

from __future__ import annotations

import os
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .config import settings


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Scene:
    id: str
    name: str
    mood: str = "neutral"     # current palette mood (evolves)
    private: bool = False     # passcode-gated
    local_only: bool = False  # block cloud providers for this scene
    created_at: str = ""


@dataclass
class Frame:
    id: str
    scene_id: Optional[str]
    title: str
    captured: str             # step 1: the moment, raw
    reflection: str = ""      # step 2: sit with (AI + user notes)
    reframe: str = ""         # step 3: reframe
    mood_score: Optional[int] = None
    created_at: str = ""
    updated_at: str = ""


class StillframeDB:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.db_path
        db_dir = os.path.dirname(self.db_path)
        if self.db_path != ":memory:" and db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        with self._lock:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS scenes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    mood TEXT DEFAULT 'neutral',
                    private INTEGER DEFAULT 0,
                    local_only INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS frames (
                    id TEXT PRIMARY KEY,
                    scene_id TEXT,
                    title TEXT NOT NULL,
                    captured TEXT NOT NULL,
                    reflection TEXT DEFAULT '',
                    reframe TEXT DEFAULT '',
                    mood_score INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS arcs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    model TEXT DEFAULT '',
                    current_stage TEXT DEFAULT '',
                    confidence REAL DEFAULT 0.0,
                    active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS arc_stage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arc_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    confirmed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 0.8,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS session_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frame_id TEXT,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS governance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_frames_scene ON frames(scene_id);
                CREATE INDEX IF NOT EXISTS idx_frames_created ON frames(created_at);
                CREATE INDEX IF NOT EXISTS idx_stage_hist_arc ON arc_stage_history(arc_id);
            """)
            self.conn.commit()

    # ── Scenes ──────────────────────────────────────────────────────────
    def create_scene(self, name: str, mood: str = "neutral",
                     private: bool = False, local_only: bool = False) -> Scene:
        scene = Scene(id=_new_id(), name=name, mood=mood, private=private,
                      local_only=local_only, created_at=_now())
        with self._lock:
            self.conn.execute(
                "INSERT INTO scenes (id, name, mood, private, local_only, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (scene.id, scene.name, scene.mood, int(scene.private),
                 int(scene.local_only), scene.created_at),
            )
            self.conn.commit()
        return scene

    def list_scenes(self) -> list[Scene]:
        with self._lock:
            rows = self.conn.execute("SELECT * FROM scenes ORDER BY created_at").fetchall()
        return [Scene(id=r["id"], name=r["name"], mood=r["mood"],
                      private=bool(r["private"]), local_only=bool(r["local_only"]),
                      created_at=r["created_at"]) for r in rows]

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        with self._lock:
            r = self.conn.execute("SELECT * FROM scenes WHERE id = ?", (scene_id,)).fetchone()
        if not r:
            return None
        return Scene(id=r["id"], name=r["name"], mood=r["mood"],
                     private=bool(r["private"]), local_only=bool(r["local_only"]),
                     created_at=r["created_at"])

    # ── Frames ──────────────────────────────────────────────────────────
    def create_frame(self, title: str, captured: str, scene_id: Optional[str] = None,
                     mood_score: Optional[int] = None) -> Frame:
        ts = _now()
        frame = Frame(id=_new_id(), scene_id=scene_id, title=title, captured=captured,
                      mood_score=mood_score, created_at=ts, updated_at=ts)
        with self._lock:
            self.conn.execute(
                "INSERT INTO frames (id, scene_id, title, captured, reflection, reframe, "
                "mood_score, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (frame.id, frame.scene_id, frame.title, frame.captured, frame.reflection,
                 frame.reframe, frame.mood_score, frame.created_at, frame.updated_at),
            )
            self.conn.commit()
        return frame

    def update_frame(self, frame_id: str, **fields) -> Optional[Frame]:
        allowed = {"title", "captured", "reflection", "reframe", "scene_id", "mood_score"}
        sets = {k: v for k, v in fields.items() if k in allowed}
        if not sets:
            return self.get_frame(frame_id)
        sets["updated_at"] = _now()
        cols = ", ".join(f"{k} = ?" for k in sets)
        with self._lock:
            self.conn.execute(f"UPDATE frames SET {cols} WHERE id = ?",
                              (*sets.values(), frame_id))
            self.conn.commit()
        return self.get_frame(frame_id)

    def get_frame(self, frame_id: str) -> Optional[Frame]:
        with self._lock:
            r = self.conn.execute("SELECT * FROM frames WHERE id = ?", (frame_id,)).fetchone()
        return self._row_to_frame(r) if r else None

    def list_frames(self, scene_id: Optional[str] = None) -> list[Frame]:
        with self._lock:
            if scene_id:
                rows = self.conn.execute(
                    "SELECT * FROM frames WHERE scene_id = ? ORDER BY created_at DESC",
                    (scene_id,)).fetchall()
            else:
                rows = self.conn.execute(
                    "SELECT * FROM frames ORDER BY created_at DESC").fetchall()
        return [self._row_to_frame(r) for r in rows]

    def delete_frame(self, frame_id: str) -> bool:
        with self._lock:
            cur = self.conn.execute("DELETE FROM frames WHERE id = ?", (frame_id,))
            self.conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _row_to_frame(r: sqlite3.Row) -> Frame:
        return Frame(
            id=r["id"], scene_id=r["scene_id"], title=r["title"], captured=r["captured"],
            reflection=r["reflection"], reframe=r["reframe"], mood_score=r["mood_score"],
            created_at=r["created_at"], updated_at=r["updated_at"],
        )

    def close(self):
        with self._lock:
            self.conn.close()


# Single app-wide instance.
db = StillframeDB()
