import sqlite3
import uuid
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger("keepalivebot.db.sqlite")

connection = sqlite3.connect('ticketbotdatabase.db')
connection.execute('PRAGMA journal_mode=WAL;')
connection.execute('PRAGMA synchronous=NORMAL;')

cursor = connection.cursor()

create_table_command = """
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    guild_id TEXT NOT NULL,
    channel_id TEXT NULL,
    creator_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    claimed_by TEXT
);
"""
cursor.execute(create_table_command)
cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_channel ON tickets(channel_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_guild_status ON tickets(guild_id, status)")


existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(tickets);").fetchall()]

def sqlite_create_ticket(guild_id, channel_id, creator_id):
    ticket_id = str(uuid.uuid4())
    created_at = datetime.now(tz=timezone.utc)
    cols = ["id", "guild_id", "channel_id", "creator_id", "status", "created_at", "claimed_by"]
    values = [ticket_id, guild_id, channel_id, creator_id, "open", created_at, None]
    placeholder = ",".join(["?"] * len(cols))
    cursor.execute(f"INSERT INTO tickets ({','.join(cols)}) VALUES ({placeholder})", values)
    connection.commit()
    return ticket_id

def sqlite_close_ticket(ticket_id):
    closed_at = datetime.now(tz=timezone.utc)
    cursor.execute("""
    UPDATE tickets
    SET status = ?, closed_at = ?
    WHERE id = ?
    """, ("closed", closed_at, ticket_id))
    connection.commit()
    return cursor.rowcount

def sqlite_get_ticket(ticket_id):
    cursor.execute("""
    SELECT * FROM tickets
    WHERE id = ?
    """, (ticket_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

def sqlite_update_ticket_status(ticket_id, status):
    cursor.execute("""
    UPDATE tickets
    SET status = ?
    WHERE id = ?
    """, (status, ticket_id))
    connection.commit()
    return cursor.rowcount

def sqlite_update_ticket_channel(ticket_id, channel_id):
    cursor.execute("""
    UPDATE tickets
    SET channel_id = ?
    WHERE id = ?
    """, (channel_id, ticket_id))
    connection.commit()
    return cursor.rowcount

def sqlite_claim_ticket(ticket_id, staff_user_id):
    cursor.execute("""
    UPDATE tickets
    SET claimed_by = ?
    WHERE id = ? AND claimed_by IS NULL
    """, (staff_user_id, ticket_id))
    connection.commit()
    rc = cursor.rowcount
    if rc == 0:
        # diagnose current claimed_by
        cursor.execute("SELECT claimed_by FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        logger.debug("sqlite_claim_ticket no-op ticket_id=%s existing_claimed_by=%s", ticket_id, row[0] if row else None)
    return rc

def sqlite_unclaim_ticket(ticket_id, staff_user_id):
    cursor.execute("""
    UPDATE tickets
    SET claimed_by = NULL
    WHERE id = ? AND claimed_by = ?
    """, (ticket_id, staff_user_id))
    connection.commit()
    rc = cursor.rowcount
    if rc == 0:
        cursor.execute("SELECT claimed_by FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        logger.debug("sqlite_unclaim_ticket no-op ticket_id=%s existing_claimed_by=%s", ticket_id, row[0] if row else None)
    return rc

def sqlite_get_ticket_id(channel_id):
    cursor.execute("""
    SELECT id FROM tickets
    WHERE channel_id = ?
    """, (channel_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def sqlite_delete_ticket(ticket_id):
    cursor.execute("""
    DELETE FROM tickets
    WHERE id = ?
    """, (ticket_id,))
    connection.commit()
    return cursor.rowcount

def sqlite_ticket_channel_exists(channel_id):
    cursor.execute("""
    SELECT 1 FROM tickets
    WHERE channel_id = ?
    """, (channel_id,))
    return cursor.fetchone() is not None

def sqlite_close():
    try:
        cursor.close()
    except Exception:
        pass
    try:
        connection.close()
    except Exception:
        pass
