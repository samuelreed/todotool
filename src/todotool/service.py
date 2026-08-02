from __future__ import annotations

from dataclasses import dataclass

from .repository import ItemRepository


class DomainError(Exception):
    pass


@dataclass
class ItemService:
    repo: ItemRepository

    def add(self, item_type: str, text: str, report: str | None) -> int:
        if item_type not in {"todo", "1on1"}:
            raise DomainError("type must be 'todo' or '1on1'.")
        if not text.strip():
            raise DomainError("text must not be empty.")
        if item_type == "todo" and report is not None:
            raise DomainError("--report is only valid for type '1on1'.")
        if item_type == "1on1" and (report is None or not report.strip()):
            raise DomainError("type '1on1' requires --report <name>.")
        return self.repo.add_item(item_type=item_type, text=text.strip(), report=report.strip() if report else None)

    def list_items(
        self,
        *,
        include_closed: bool,
        include_archived: bool,
        item_type: str | None,
        report: str | None,
        keyword: str | None = None,
    ):
        if item_type is not None and item_type not in {"todo", "1on1"}:
            raise DomainError("--type must be 'todo' or '1on1'.")
        if report is not None and item_type == "todo":
            raise DomainError("--report cannot be used with --type todo.")
        return self.repo.query_items(
            include_closed=include_closed,
            include_archived=include_archived,
            item_type=item_type,
            report=report,
            keyword=keyword,
        )

    def complete(self, item_id: int) -> None:
        item = self.repo.get_item(item_id)
        if item is None:
            raise DomainError(f"item {item_id} not found.")
        if item["type"] != "todo":
            raise DomainError(f"item {item_id} is type '{item['type']}', not todo.")
        if item["status"] != "open":
            raise DomainError(f"item {item_id} is already {item['status']}.")
        self.repo.set_status(item_id, "completed")

    def relay(self, item_id: int) -> None:
        item = self.repo.get_item(item_id)
        if item is None:
            raise DomainError(f"item {item_id} not found.")
        if item["type"] != "1on1":
            raise DomainError(f"item {item_id} is type '{item['type']}', not 1on1.")
        if item["status"] != "open":
            raise DomainError(f"item {item_id} is already {item['status']}.")
        self.repo.set_status(item_id, "relayed")

    def archive(self, item_id: int) -> None:
        item = self.repo.get_item(item_id)
        if item is None:
            raise DomainError(f"item {item_id} not found.")
        if item["archived"] == 1:
            raise DomainError(f"item {item_id} is already archived.")
        self.repo.archive_item(item_id)
