from __future__ import annotations

import sqlite3
from typing import Any


class ItemRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_item(self, item_type: str, text: str, report: str | None) -> int:
        cur = self.conn.execute(
            "INSERT INTO items(type, text, report, status, archived) VALUES(?, ?, ?, 'open', 0)",
            (item_type, text, report),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_item(self, item_id: int) -> sqlite3.Row | None:
        cur = self.conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        return cur.fetchone()

    def set_status(self, item_id: int, status: str) -> None:
        self.conn.execute(
            "UPDATE items SET status = ?, closed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, item_id),
        )
        self.conn.commit()

    def archive_item(self, item_id: int) -> None:
        self.conn.execute(
            "UPDATE items SET archived = 1, archived_at = CURRENT_TIMESTAMP WHERE id = ?",
            (item_id,),
        )
        self.conn.commit()

    def query_items(
        self,
        *,
        include_closed: bool,
        include_archived: bool,
        item_type: str | None,
        report: str | None,
        keyword: str | None,
    ) -> list[dict[str, Any]]:
        where: list[str] = []
        params: list[Any] = []

        if not include_closed:
            where.append("status = 'open'")
        if not include_archived:
            where.append("archived = 0")
        if item_type is not None:
            where.append("type = ?")
            params.append(item_type)
        if report is not None:
            where.append("report = ?")
            params.append(report)
        if keyword is not None:
            where.append("(text LIKE ? OR COALESCE(report, '') LIKE ?)")
            like = f"%{keyword}%"
            params.extend([like, like])

        sql = "SELECT id, type, text, report, status, archived, created_at, updated_at FROM items"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY archived ASC, status ASC, id DESC"

        cur = self.conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        for row in rows:
            row["archived"] = bool(row["archived"])
        return rows
