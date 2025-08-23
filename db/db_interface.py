from dotenv import load_dotenv
import os
from db.mongodb import (
    mongo_create_ticket,
    mongo_close_ticket,
    mongo_get_ticket,
    mongo_update_ticket_status,
    mongo_update_ticket_channel,
    mongo_get_ticket_id,
    mongo_delete_ticket,
    mongo_ticket_channel_exists,
    mongo_claim_ticket,
    mongo_unclaim_ticket,
)
from db.sqllite import (
    sqlite_create_ticket,
    sqlite_close_ticket,
    sqlite_get_ticket,
    sqlite_update_ticket_status,
    sqlite_update_ticket_channel,
    sqlite_get_ticket_id,
    sqlite_delete_ticket,
    sqlite_ticket_channel_exists,
    sqlite_claim_ticket,
    sqlite_unclaim_ticket,
)
from db.mysql import (
    mysql_create_ticket,
    mysql_close_ticket,
    mysql_get_ticket,
    mysql_update_ticket_status,
    mysql_update_ticket_channel,
    mysql_get_ticket_id,
    mysql_delete_ticket,
    mysql_ticket_channel_exists,
    mysql_claim_ticket,
    mysql_unclaim_ticket
)

load_dotenv()

mongo = False
sqlite = False
mysql = False

db_type = os.getenv("DB_TYPE")

if db_type == "mongodb":
    mongo = True
elif db_type == "sqlite":
    sqlite = True
elif db_type == "mysql":
    mysql = True

def db_create_ticket(guild_id, channel_id, creator_id):
    if mongo:
        return mongo_create_ticket(guild_id, channel_id, creator_id)
    elif sqlite:
        return sqlite_create_ticket(guild_id, channel_id, creator_id)
    elif mysql:
        return mysql_create_ticket(guild_id, channel_id, creator_id)

def db_close_ticket(ticket_id):
    if mongo:
        return mongo_close_ticket(ticket_id)
    elif sqlite:
        return sqlite_close_ticket(ticket_id)
    elif mysql:
        return mysql_close_ticket(ticket_id)
    
def db_get_ticket(ticket_id):
    if mongo:
        return mongo_get_ticket(ticket_id)
    elif sqlite:
        return sqlite_get_ticket(ticket_id)
    elif mysql:
        return mysql_get_ticket(ticket_id)

def db_update_ticket_status(ticket_id, status):
    if mongo:
        return mongo_update_ticket_status(ticket_id, status)
    elif sqlite:
        return sqlite_update_ticket_status(ticket_id, status)
    elif mysql:
        return mysql_update_ticket_status(ticket_id, status)
    
def db_update_ticket_channel(ticket_id, channel_id):
    if mongo:
        return mongo_update_ticket_channel(ticket_id, channel_id)
    elif sqlite:
        return sqlite_update_ticket_channel(ticket_id, channel_id)
    elif mysql:
        return mysql_update_ticket_channel(ticket_id, channel_id)

def db_get_ticket_id(channel_id):
    if mongo:
        return mongo_get_ticket_id(channel_id)
    elif sqlite:
        return sqlite_get_ticket_id(channel_id)
    elif mysql:
        return mysql_get_ticket_id(channel_id)
    
def db_delete_ticket(ticket_id):
    if mongo:
        return mongo_delete_ticket(ticket_id)
    elif sqlite:
        return sqlite_delete_ticket(ticket_id)
    elif mysql:
        return mysql_delete_ticket(ticket_id)

def db_ticket_channel_exists(channel_id):
    if mongo:
        return mongo_ticket_channel_exists(channel_id)
    elif sqlite:
        return sqlite_ticket_channel_exists(channel_id)
    elif mysql:
        return mysql_ticket_channel_exists(channel_id)

def db_claim_ticket(ticket_id, staff_user_id):
    if mongo:
        return mongo_claim_ticket(ticket_id, staff_user_id)
    elif sqlite:
        return sqlite_claim_ticket(ticket_id, staff_user_id)
    elif mysql:
        return mysql_claim_ticket(ticket_id, staff_user_id)

def db_unclaim_ticket(ticket_id, staff_user_id):
    if mongo:
        return mongo_unclaim_ticket(ticket_id, staff_user_id)
    elif sqlite:
        return sqlite_unclaim_ticket(ticket_id, staff_user_id)
    elif mysql:
        return mysql_unclaim_ticket(ticket_id, staff_user_id)
