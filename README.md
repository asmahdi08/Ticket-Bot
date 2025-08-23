# Ticket Bot

A focused Discord ticketing bot built with Python (discord.py) supporting multiple database backends (SQLite, MySQL, MongoDB). Clean slash commands, claim system, per‑ticket private channels, and production‑ready structure.

## Features

### 🎫 Ticket System
- Create private ticket channels with controlled access
- Close / delete tickets with audit logging
- Add / remove participants dynamically
- Claim & unclaim tickets (staff ownership tracking)
- Ticket info command (status, creator, claimer)

### 🗄️ Multiple Database Backends
Select at runtime via `DB_TYPE` env var:
- **sqlite** – Zero‑config local persistence (WAL enabled for better concurrency)
- **mysql** – Auto database creation & indexed queries
- **mongodb** – Document store support

### ⚙️ Operational Quality
- Graceful shutdown closes DB connections cleanly
- Structured logging (file + console) with optional DEBUG mode (`DEBUG=1`)
- Environment validation on startup

## Roadmap (Optional Enhancements)
- Transcript export
- Ticket reopen
- Archive / purge commands
- Staff analytics

## Installation

### Prerequisites
- Python 3.11+ (tested on 3.13)
- Discord Bot Token (with applications.commands scope)
- One of: SQLite (bundled) / MySQL server / MongoDB cluster

### Clone
```bash
git clone https://github.com/asmahdi08/Ticket-Bot.git
cd Ticket-Bot
```

### (Recommended) Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

### Install Dependencies
Install core libs (adjust if you drop unused backends):
```bash
pip install discord.py python-dotenv pymongo mysql-connector-python
```

### Environment Variables

Take a look at the .env.example file

### Run
```bash
python bot.py
```

## Slash Commands (Guild Scoped)

All ticket commands are restricted to users with the support role:
- `/ticket setup` – Post the ticket creation embed with button
- `/ticket create` – Manually create a ticket for yourself
- `/ticket close` – Close a ticket (locks creator replies)
- `/ticket delete` – Delete ticket channel + DB record
- `/ticket add <user>` – Add a participant
- `/ticket remove <user>` – Remove a participant
- `/ticket claim` – Claim the ticket (sets you as handler)
- `/ticket unclaim` – Relinquish claim
- `/ticket info` – Show metadata (id, status, creator, claimed_by)

Ticket channels are named `ticket-<short-id>` and only visible to the creator + support staff.
The `<short-id>` is basically the first part of the id string generated using python uuid

## Architecture

### Core Modules
- `bot.py` – Startup, logging, env validation, graceful shutdown
- `cogs/TicketCog.py` – Slash command group & interaction logic
- `utils/botutils.py` – Ticket channel + DB orchestration helpers
- `utils/embeds.py` – Embed functions
- `ui/TicketSetupView.py` – Persistent view with “Open Ticket” button
- `db/` backends – `sqllite.py`, `mysql.py`, `mongodb.py` + `db_interface.py` for abstraction

### Data Model (Conceptual)
| Field | Meaning |
|-------|---------|
| id | UUID ticket identifier |
| guild_id | Owning guild ID |
| channel_id | Discord channel ID (set after creation) |
| creator_id | User who opened ticket |
| status | `open` / `closed` |
| created_at | UTC timestamp |
| closed_at | UTC timestamp on close |
| claimed_by | Staff member ID or null |

Indexes (MySQL/SQLite) on `channel_id` and composite `(guild_id, status)` for faster lookups.

## Technical Notes

### Command Sync
Guild-specific sync is performed once per process run; this avoids global command propagation delay and rate limits.

### Graceful Shutdown
SIGINT / SIGTERM handlers close DB connections (SQLite & MySQL). MongoDB client is managed by driver and closes on process exit.

### Debug Logging
Enable granular debug with `DEBUG=1` to see claim diagnostics and DB row counts.

## Troubleshooting and Issues

**Post on the Github Repo Issues section**

## Contributing
Contributions are welcome. Keep changes small and documented. Add/update README sections when touching public behavior.

## License
MIT – see [LICENSE](LICENSE).

## Support
Open a GitHub issue or contact the maintainer.

---
Made for Discord support teams.
