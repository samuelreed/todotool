from __future__ import annotations

import sys
from pathlib import Path

from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from todotool.cli import app

runner = CliRunner()


def test_1on1_requires_report(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    result = runner.invoke(app, ["add", "--type", "1on1", "Discuss growth plan"])
    assert result.exit_code != 0


def test_default_list_shows_open_non_archived_only(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    assert runner.invoke(app, ["add", "Ship Q3 draft"]).exit_code == 0
    assert runner.invoke(
        app, ["add", "--type", "1on1", "--report", "alex", "Promotion timeline"]
    ).exit_code == 0

    out = runner.invoke(app, ["list"])
    assert out.exit_code == 0
    assert "Ship Q3 draft" in out.stdout
    assert "Promotion timeline" in out.stdout


def test_complete_and_relay_type_rules_and_closed_filter(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    runner.invoke(app, ["add", "Close expense follow-up"])
    runner.invoke(app, ["add", "--type", "1on1", "--report", "sam", "Talk about onboarding"])

    wrong_complete = runner.invoke(app, ["complete", "2"])
    assert wrong_complete.exit_code != 0

    wrong_relay = runner.invoke(app, ["relay", "1"])
    assert wrong_relay.exit_code != 0

    assert runner.invoke(app, ["complete", "1"]).exit_code == 0
    assert runner.invoke(app, ["relay", "2"]).exit_code == 0

    default_list = runner.invoke(app, ["list"])
    assert "No items found." in default_list.stdout

    closed_list = runner.invoke(app, ["list", "--closed"])
    assert "Close expense follow-up" in closed_list.stdout
    assert "Talk about onboarding" in closed_list.stdout


def test_archived_hidden_unless_archived_flag(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    runner.invoke(app, ["add", "Prepare roadmap doc"])
    runner.invoke(app, ["archive", "1"])

    default_list = runner.invoke(app, ["list"])
    assert "Prepare roadmap doc" not in default_list.stdout

    archived_list = runner.invoke(app, ["list", "--archived"])
    assert "Prepare roadmap doc" in archived_list.stdout


def test_search_respects_closed_and_archived_filters(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    runner.invoke(app, ["add", "Release checklist"])
    runner.invoke(app, ["complete", "1"])
    runner.invoke(app, ["add", "Release notes"])
    runner.invoke(app, ["archive", "2"])

    default_search = runner.invoke(app, ["search", "Release"])
    assert "No items found." in default_search.stdout

    closed_search = runner.invoke(app, ["search", "Release", "--closed"])
    assert "Release checklist" in closed_search.stdout
    assert "Release notes" not in closed_search.stdout

    archived_search = runner.invoke(app, ["search", "Release", "--archived"])
    assert "Release notes" in archived_search.stdout
    assert "Release checklist" not in archived_search.stdout

    all_search = runner.invoke(app, ["search", "Release", "--closed", "--archived"])
    assert "Release checklist" in all_search.stdout
    assert "Release notes" in all_search.stdout
