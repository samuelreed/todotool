# Implementation Plan

## Project Goal
Build a command-line tool that helps a manager track two kinds of recurring work:

1. Quick todo items entered from the command line and stored in a SQLite database.
2. 1-on-1 discussion items that can be captured, reviewed, and marked as relayed during regular check-ins.

The tool should be simple, fast to use, and reliable for repeated daily use.

## Core Functionalities

### Unified item tracking
All items (todos and 1-on-1 topics) are stored as a single object type with a `type` field distinguishing them.

#### Common features for all items
- Add a new item from the command line.
- List open items by default (closed items hidden unless explicitly requested).
- Mark an item as complete/relayed based on type.
- Archive items to hide them from both open and closed lists.
- Search items by keyword in title/description.

#### 1. Todo tracking
- Add a todo with a short description.
- Support status: open or completed.
- Mark as complete.

#### 2. 1-on-1 agenda tracking
- Add a discussion item for a specific report or 1-on-1 context.
- Support status: open or relayed.
- Mark as relayed once the discussion has been covered in the meeting.
- List outstanding items for a given report or across all reports.

## Proposed CLI Shape
The tool should expose commands such as:
- `item add --type todo <description>` (shorthand: `ia -t todo <description>`)
- `item add --type 1on1 --report <name> <topic>` (shorthand: `ia -t 1on1 -r <name> <topic>`)
- `item list [--closed] [--archived] [--type todo|1on1] [--report <name>]` (shorthand: `il`)
- `item complete <id>` (shorthand: `ic <id>`)
- `item relay <id>` (shorthand: `ir <id>`)
- `item archive <id>` (shorthand: `iarch <id>`)
- `item search <keyword> [--closed] [--archived]` (shorthand: `is <keyword>`)
- Interactive mode: `item review [--report <name>]` (shorthand: `irev`) to quickly mark items as complete/relayed

## Data Model
Single unified table with a type field:

```
items(
  id (primary key),
  type (todo | 1on1),
  title (string),
  description (string),
  status (open | completed | relayed),
  created_at (timestamp),
  completed_at (timestamp, nullable),
  archived (boolean, default false),
  report (string, nullable - used for 1on1 items),
  link (string, nullable - URL to Jira, Trello, or other external resource)
)
```

The `status` field handles both todo and 1on1 states:
- Todo: open → completed
- 1on1: open → relayed

The `archived` flag removes items from both open and closed views unless explicitly queried.

## Implementation Scope for the First Version
Keep the first version small and focused:
- Single executable CLI entry point
- SQLite-backed persistence with unified `items` table at `~/.todotool/items.db`
- Config file at `~/.todotool/config.yaml` with auto-archive settings (disabled by default)
- Unified data model with type field (todo, 1on1)
- Archived flag for hiding items
- Basic add/list/update/archive/search flows with auto-incrementing integer IDs
- Search by keyword in title and description
- Report filtering for 1on1 items (e.g., `item list --report <name>`)
- Command shortcuts for fast entry (e.g., `ia`, `il`, `ic`, `ir`, `iarch`, `is`, `irev`)
- Human-readable CLI output by default; JSON output with --json flag
- Interactive review mode for quick status updates during 1on1s
- Minimal dependencies
- Clear help output and sensible defaults
- List command hides archived items by default; --archived flag shows all

## Decisions Made
1. **List behavior:** `item list` with no flags shows only open, non-archived items. Closed and archived items are hidden unless explicitly requested with --closed or --archived flags.
2. **Default behavior:** Start with open items by default. Provide options to search closed and archived items when needed.
3. **Auto-archive:** Implement a config file that specifies the age of a ticket for auto-archiving. This feature is disabled by default but can be enabled and configured by the user.
4. **Config & database location:** Both config and SQLite database live in `~/.todotool/`. (Config: `~/.todotool/config.yaml`, Database: `~/.todotool/items.db`)
5. **ID scheme:** Use auto-incrementing integers for item IDs.
6. **Output format:** CLI output is human-readable by default. JSON output only available with --json flag.
7. **Report filtering:** Support filtering 1on1 items by a specific report using a flag (e.g., `item list --report <name>`). This will be used to generate agendas for 1on1 meetings.
8. **Command shortcuts:** Support both shorthand (e.g., `ia` for `item add`) and full-form readable commands.
9. **Interactive mode:** Include both interactive workflow and straight CLI commands for flexibility.

## Architecture & Technology Stack
- **Language:** Python 3.8+
- **CLI framework:** Click for command parsing and argument handling
- **Console UI:** Rich library for enhanced console UI capabilities and tabular output formatting
- **Database:** SQLite with SQLAlchemy ORM for long-term maintenance and flexibility
- **Config parsing:** PyYAML for YAML config file handling
- **Interactive mode:** Rich + prompt_toolkit for enhanced interactive review workflow
- **Error handling:** Human-readable error messages sent to stderr; no logging framework at this stage
- **Testing:** pytest with light, focused tests; no heavy frameworks or complex test infrastructure
- **Packaging:** Python script installable via pip; entry point console script for easy CLI access
- **Directory structure:** Follow GitHub best practices (src/, tests/, README.md, setup.py/pyproject.toml, etc.)
- **Platform support:** macOS and Linux (no Windows-specific features required)
- **Auto-archive:** Manual command (`item archive-old [--days N]`) to trigger auto-archiving based on config or explicit age threshold
- **CI/CD:** None at this stage; no GitHub Actions or automated checks

## Success Criteria
The first version is successful if a user can:
- quickly add a todo from the terminal (using full command or shorthand)
- quickly add a 1-on-1 discussion item with a report name (using full command or shorthand)
- view open items (todos and 1on1s, non-archived) with human-readable output
- filter items by report for 1on1s
- view closed items with --closed flag
- mark a todo as complete
- mark a 1on1 item as relayed
- archive an item to remove it from view
- search for items by keyword
- use interactive mode to quickly review and update item statuses
- rely on SQLite persistence across runs
- configure auto-archive behavior via config file

## Notes
- Keep the experience fast and keyboard-friendly.
- Avoid over-engineering early; implement the smallest useful set first.
- Update this plan as decisions are made.
