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
- One‑time command sync to avoid Discord rate limits
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
Create a `.env` file in the project root:
```env
BOT_TOKEN=your_discord_bot_token
GUILD_ID=123456789012345678
SUPPORT_ROLE_ID=123456789012345678
DB_TYPE=sqlite            # one of: sqlite | mysql | mongodb

# MySQL (if DB_TYPE=mysql)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=secret
MYSQL_DATABASE=ticket_bot

# MongoDB (if DB_TYPE=mongodb)
MONGO_URI=mongodb+srv://user:pass@cluster/url
MONGO_DB_NAME=ticket_bot

# Optional
DEBUG=0  # set to 1 for verbose debug logging
```

### Run
```bash
python bot.py
```

If command sync logs 429 warnings, leave the bot running—subsequent starts won’t re-sync unless code changes (guarded in `bot.py`).

## Slash Commands (Guild Scoped)

All ticket commands are restricted to users with the support role:
- `/ticket setup` – Post the ticket creation panel with button
- `/ticket create` – Manually create a ticket for yourself
- `/ticket close` – Close a ticket (locks creator replies)
- `/ticket delete` – Delete ticket channel + DB record
- `/ticket add <user>` – Add a participant
- `/ticket remove <user>` – Remove a participant
- `/ticket claim` – Claim the ticket (sets you as handler)
- `/ticket unclaim` – Relinquish claim
- `/ticket info` – Show metadata (id, status, creator, claimed_by)

Ticket channels are named `ticket-<short-id>` and only visible to the creator + support staff.

## Architecture

### Core Modules
- `bot.py` – Startup, logging, env validation, graceful shutdown
- `cogs/TicketCog.py` – Slash command group & interaction logic
- `utils/botutils.py` – Ticket channel + DB orchestration helpers
- `utils/embeds.py` – Embed factories (create / close / claim)
- `ui/TicketSetupView.py` – Persistent view with “Open Ticket” button
- `db/` backends – `sqllite.py`, `mysql.py`, `mongodb.py` + `db_interface.py` router

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

### SQLite WAL Files
`ticketbotdatabase.db-wal` and `.db-shm` are normal when WAL mode is enabled; they enhance concurrency. To revert to a single file, remove the WAL pragma in `db/sqllite.py`.

### Command Sync
Guild-specific sync is performed once per process run; this avoids global command propagation delay and rate limits.

### Graceful Shutdown
SIGINT / SIGTERM handlers close DB connections (SQLite & MySQL). MongoDB client is managed by driver and closes on process exit.

### Debug Logging
Enable granular debug with `DEBUG=1` to see claim diagnostics and DB row counts.

## Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| 404 Unknown Channel on delete | Respond after deletion attempted | Fixed: we respond before deleting now |
| Ticket claim always “already claimed” | Existing claimed_by or rowcount 0 | Use DEBUG=1 to view diagnostics |
| MySQL unknown database | DB absent | Auto-creation handled; verify credentials |
| Extra SQLite `-wal`/`-shm` files | WAL mode active | Accept (normal) or disable WAL |

## Contributing
PRs & issues welcome. Keep changes small and documented. Add/update README sections when touching public behavior.

## License
MIT – see [LICENSE](LICENSE).

## Support
Open a GitHub issue or contact the maintainer.

---
Made for Discord support teams.
