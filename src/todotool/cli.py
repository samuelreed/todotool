from __future__ import annotations

import json
from typing import Optional

import typer

from .db import get_connection
from .repository import ItemRepository
from .service import DomainError, ItemService

app = typer.Typer(help="Todo + 1on1 CLI")


def _service() -> ItemService:
    conn = get_connection()
    return ItemService(repo=ItemRepository(conn))


def _fail(message: str) -> None:
    typer.secho(f"Error: {message}", err=True, fg=typer.colors.RED)
    raise typer.Exit(code=1)


def _render(items: list[dict], as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(items, indent=2))
        return
    if not items:
        typer.echo("No items found.")
        return

    for item in items:
        report_part = f" report={item['report']}" if item["report"] else ""
        archived_part = " archived" if item["archived"] else ""
        typer.echo(
            f"[{item['id']}] {item['type']} {item['status']}{archived_part}{report_part} :: {item['text']}"
        )


@app.command("add")
def add_command(
    text: str = typer.Argument(..., help="Item text"),
    item_type: str = typer.Option("todo", "--type", help="todo or 1on1"),
    report: Optional[str] = typer.Option(None, "--report", help="Report name for 1on1"),
) -> None:
    svc = _service()
    try:
        item_id = svc.add(item_type=item_type, text=text, report=report)
    except DomainError as exc:
        _fail(str(exc))
    typer.echo(f"Added item {item_id}.")


@app.command("list")
def list_command(
    closed: bool = typer.Option(False, "--closed", help="Include closed items"),
    archived: bool = typer.Option(False, "--archived", help="Include archived items too"),
    item_type: Optional[str] = typer.Option(None, "--type", help="Filter by todo or 1on1"),
    report: Optional[str] = typer.Option(None, "--report", help="Filter by report"),
    as_json: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    svc = _service()
    try:
        items = svc.list_items(
            include_closed=closed,
            include_archived=archived,
            item_type=item_type,
            report=report,
        )
    except DomainError as exc:
        _fail(str(exc))
    _render(items, as_json=as_json)


@app.command("complete")
def complete_command(item_id: int = typer.Argument(..., help="Todo item id")) -> None:
    svc = _service()
    try:
        svc.complete(item_id)
    except DomainError as exc:
        _fail(str(exc))
    typer.echo(f"Completed item {item_id}.")


@app.command("relay")
def relay_command(item_id: int = typer.Argument(..., help="1on1 item id")) -> None:
    svc = _service()
    try:
        svc.relay(item_id)
    except DomainError as exc:
        _fail(str(exc))
    typer.echo(f"Relayed item {item_id}.")


@app.command("archive")
def archive_command(item_id: int = typer.Argument(..., help="Item id")) -> None:
    svc = _service()
    try:
        svc.archive(item_id)
    except DomainError as exc:
        _fail(str(exc))
    typer.echo(f"Archived item {item_id}.")


@app.command("search")
def search_command(
    keyword: str = typer.Argument(..., help="Keyword"),
    closed: bool = typer.Option(False, "--closed", help="Include closed items"),
    archived: bool = typer.Option(False, "--archived", help="Include archived items too"),
    as_json: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    svc = _service()
    try:
        items = svc.list_items(
            include_closed=closed,
            include_archived=archived,
            item_type=None,
            report=None,
            keyword=keyword,
        )
    except DomainError as exc:
        _fail(str(exc))
    _render(items, as_json=as_json)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
