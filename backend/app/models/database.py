"""SQLite connection management and schema creation.

Kept deliberately simple for an MVP: one file, a handful of tables, no ORM.
Each function opens and closes its own connection so callers (including
tests, which point LUMI_DATABASE_PATH at a temp file) never have to manage
connection lifetime.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.config import DATABASE_PATH, DEMO_USER_ID, SUPPORTED_SOURCES


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_cursor() -> Iterator[sqlite3.Cursor]:
    """Context manager yielding a cursor; commits on success, closes always."""

    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        conn.close()


def _ensure_column(cur: sqlite3.Cursor, table: str, column: str, ddl_type_and_default: str) -> None:
    """Add a column if it's missing, without touching existing data.

    Lets init_db() stay idempotent even when a database file created by an
    earlier phase already has the table but not this column.
    """

    cur.execute(f"PRAGMA table_info({table})")
    existing_columns = {row[1] for row in cur.fetchall()}
    if column not in existing_columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type_and_default}")


def init_db() -> None:
    """Create all tables if they don't already exist, and seed permissions."""

    with db_cursor() as cur:
        # Raw incoming data items. Only rows with permission=1 ever carry a
        # populated `data` payload — see app/permissions/service.py. Rows
        # with permission=0 are kept only as an audit trail (empty data),
        # mirroring device-hub's own denied-result shape.
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS data_items (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                permission INTEGER NOT NULL,
                data TEXT NOT NULL
            )
            """
        )

        # Personal memory. The API-facing shape (see Memory schema) is
        # exactly {id, content, source, timestamp, importance} — user_id is
        # an internal scoping column only, never returned to callers, and
        # exists so this table is already multi-user-shaped without us
        # building real auth right now (see DEMO_USER_ID in app/config.py).
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'demo-user',
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance REAL NOT NULL
            )
            """
        )
        _ensure_column(cur, "memories", "user_id", f"TEXT NOT NULL DEFAULT '{DEMO_USER_ID}'")

        # Conversation history is separate from personal memories and has no
        # source permission semantics. It is scoped to the current user.
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

        # Per-source permission state. Defaults to disabled, same as
        # device-hub's PermissionManager, so a source is never usable
        # until the user explicitly opts in.
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS permissions (
                source TEXT PRIMARY KEY,
                permission INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # Uploaded documents and their chunks (Phase 4 / RAG).
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding TEXT
            )
            """
        )

        # Seed every known source as disabled if it isn't already present.
        for source in sorted(SUPPORTED_SOURCES):
            cur.execute(
                "INSERT OR IGNORE INTO permissions (source, permission) VALUES (?, 0)",
                (source,),
            )


def reset_db() -> None:
    """Drop and recreate all tables. Used by tests for a clean slate."""

    with db_cursor() as cur:
        for table in (
            "document_chunks",
            "documents",
            "chat_messages",
            "memories",
            "data_items",
            "permissions",
        ):
            cur.execute(f"DROP TABLE IF EXISTS {table}")
    init_db()
