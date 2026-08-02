from __future__ import annotations

import sqlite3
from pathlib import Path


def app_dir() -> Path:
    return Path.home() / ".todotool"


def db_path() -> Path:
    return app_dir() / "items.db"


def _schema_sql() -> str:
    return """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        text TEXT NOT NULL,
        report TEXT,
        status TEXT NOT NULL DEFAULT 'open',
        archived INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        closed_at TEXT,
        archived_at TEXT,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CHECK (type IN ('todo', '1on1')),
        CHECK (status IN ('open', 'completed', 'relayed')),
        CHECK (archived IN (0, 1)),
        CHECK (
            (type = 'todo' AND report IS NULL AND status IN ('open', 'completed')) OR
            (type = '1on1' AND report IS NOT NULL AND trim(report) <> '' AND status IN ('open', 'relayed'))
        ),
        CHECK (trim(text) <> '')
    );

    CREATE INDEX IF NOT EXISTS idx_items_status_archived ON items(status, archived);
    CREATE INDEX IF NOT EXISTS idx_items_type ON items(type);
    CREATE INDEX IF NOT EXISTS idx_items_report ON items(report);

    CREATE TRIGGER IF NOT EXISTS trg_items_updated_at
    AFTER UPDATE ON items
    FOR EACH ROW
    BEGIN
      UPDATE items SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """


def get_connection() -> sqlite3.Connection:
    app_dir().mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.executescript(_schema_sql())
    return conn
