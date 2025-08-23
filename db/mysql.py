import mysql.connector
from mysql.connector import Error
from datetime import datetime, timezone
import uuid
import os
import logging

logger = logging.getLogger("keepalivebot.db.mysql")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ticket_bot")

def _connect_db(database: str | None = MYSQL_DATABASE):
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database
    ) if database else mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )

try:
    connection = _connect_db()
except Error as e:
    if getattr(e, 'errno', None) == 1049:  # Unknown database
        logger.info("Database %s missing, creating it", MYSQL_DATABASE)
        tmp_conn = _connect_db(database=None)
        tmp_cursor = tmp_conn.cursor()
        tmp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        tmp_cursor.close()
        tmp_conn.close()
        connection = _connect_db()
    else:
        raise

cursor = connection.cursor(dictionary=True)

create_table_command = (
    """
    CREATE TABLE IF NOT EXISTS tickets (
        id VARCHAR(36) PRIMARY KEY,
        guild_id BIGINT NOT NULL,
        channel_id BIGINT,
        creator_id BIGINT NOT NULL,
        status VARCHAR(16) NOT NULL,
        created_at DATETIME NOT NULL,
        closed_at DATETIME,
        claimed_by BIGINT,
        KEY idx_channel (channel_id),
        KEY idx_guild_status (guild_id, status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
)
cursor.execute(create_table_command)
connection.commit()

def mysql_create_ticket(guild_id, channel_id, creator_id):
    ticket_id = str(uuid.uuid4())
    created_at = datetime.now(tz=timezone.utc)
    cursor.execute("""
    INSERT INTO tickets (id, guild_id, channel_id, creator_id, status, created_at, claimed_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (ticket_id, guild_id, channel_id, creator_id, "open", created_at, None))
    connection.commit()
    return ticket_id

def mysql_close_ticket(ticket_id):
    closed_at = datetime.now(tz=timezone.utc)
    cursor.execute("""
    UPDATE tickets
    SET status = %s, closed_at = %s
    WHERE id = %s
    """, ("closed", closed_at, ticket_id))
    connection.commit()
    return cursor.rowcount

def mysql_get_ticket(ticket_id):
    cursor.execute("""
    SELECT * FROM tickets
    WHERE id = %s
    """, (ticket_id,))
    row = cursor.fetchone()
    # With dictionary=True cursor, row is already a dict
    return row if row else None

def mysql_update_ticket_status(ticket_id, status):
    cursor.execute("""
    UPDATE tickets
    SET status = %s
    WHERE id = %s
    """, (status, ticket_id))
    connection.commit()
    return cursor.rowcount

def mysql_update_ticket_channel(ticket_id, channel_id):
    cursor.execute("""
    UPDATE tickets
    SET channel_id = %s
    WHERE id = %s
    """, (channel_id, ticket_id))
    connection.commit()
    return cursor.rowcount

def mysql_claim_ticket(ticket_id, staff_user_id):
    cursor.execute("""
    UPDATE tickets
    SET claimed_by = %s
    WHERE id = %s AND claimed_by IS NULL
    """, (staff_user_id, ticket_id))
    connection.commit()
    rc = cursor.rowcount
    if rc == 0:
        cursor.execute("SELECT claimed_by FROM tickets WHERE id = %s", (ticket_id,))
        row = cursor.fetchone()
        logger.debug("mysql_claim_ticket no-op ticket_id=%s existing_claimed_by=%s", ticket_id, row[0] if row else None)
    return rc

def mysql_unclaim_ticket(ticket_id, staff_user_id):
    cursor.execute("""
    UPDATE tickets
    SET claimed_by = NULL
    WHERE id = %s AND claimed_by = %s
    """, (ticket_id, staff_user_id))
    connection.commit()
    rc = cursor.rowcount
    if rc == 0:
        cursor.execute("SELECT claimed_by FROM tickets WHERE id = %s", (ticket_id,))
        row = cursor.fetchone()
        logger.debug("mysql_unclaim_ticket no-op ticket_id=%s existing_claimed_by=%s", ticket_id, row[0] if row else None)
    return rc

def mysql_get_ticket_id(channel_id):
    cursor.execute("""
    SELECT id FROM tickets
    WHERE channel_id = %s
    """, (channel_id,))
    row = cursor.fetchone()
    if not row:
        return None
    # row is dict because dictionary=True
    return row.get("id")

def mysql_delete_ticket(ticket_id):
    cursor.execute("""
    DELETE FROM tickets
    WHERE id = %s
    """, (ticket_id,))
    connection.commit()
    return cursor.rowcount

def mysql_ticket_channel_exists(channel_id):
    cursor.execute("""
    SELECT 1 FROM tickets
    WHERE channel_id = %s
    """, (channel_id,))
    return cursor.fetchone() is not None

def mysql_get_ticket_by_channel(channel_id):
    cursor.execute("""
    SELECT * FROM tickets
    WHERE channel_id = %s
    """, (channel_id,))
    return cursor.fetchone()

def mysql_close():
    try:
        cursor.close()
    except Exception:
        pass
    try:
        connection.close()
    except Exception:
        pass
