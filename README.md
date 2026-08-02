# todotool (POC)

Small Typer CLI for tracking todo + 1on1 items.

## Quickstart

```bash
python -m pip install -e .
item add "Draft roadmap"
item add --type 1on1 --report alex "Discuss promotion packet"
item list
item complete 1
item relay 2
item list --closed
item archive 1
item list --archived
item search roadmap --closed --archived
```

## Behavior

- `list`/`search` default to open + non-archived items.
- `--closed` includes `completed` + `relayed`.
- `--archived` includes archived items.
- `complete` only works for `todo`.
- `relay` only works for `1on1`.
- `add --type 1on1` requires `--report`.

Data is stored at `~/.todotool/items.db`.

## Notes
This repo is a test of using VS Code agent mode. I wanted to see what the experience was like. I had generally minimal correction on that agents as they ran; hopefully nothing embarssing is being checked in that I missed during review. I produced only IMPLEMENTATION_PLAN.md. This first checkin is 100% agent produced.