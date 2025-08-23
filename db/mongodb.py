from pymongo import MongoClient
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# connect to mongodb
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]

ticketbotdb = db.ticketbot
ticketscollection = db.tickets



def mongo_create_ticket(guild_id, channel_id, creator_id):
    ticket_id = str(uuid.uuid4())
    ticketdoc = {
        "_id": ticket_id,
        "guild_id": guild_id,
        "channel_id": channel_id,
        "creator_id": creator_id,
        "status": "open", # open, closed
        "created_at": datetime.now(tz=timezone.utc),
    "closed_at": None,
    "claimed_by": None,
    }
    ticketscollection.insert_one(ticketdoc)
    return ticket_id

def mongo_close_ticket(ticket_id):
    result = ticketscollection.update_one({"_id": ticket_id}, {"$set": {"status": "closed", "closed_at": datetime.now(tz=timezone.utc )}})
    return result.modified_count

def mongo_get_ticket(ticket_id):
    return ticketscollection.find_one({"_id": ticket_id})

def mongo_update_ticket_status(ticket_id, status):
    result = ticketscollection.update_one({"_id": ticket_id}, {"$set": {"status": status}})
    return result.modified_count

def mongo_update_ticket_channel(ticket_id, channel_id):
    result = ticketscollection.update_one({"_id": ticket_id}, {"$set": {"channel_id": channel_id}})
    return result.modified_count

def mongo_claim_ticket(ticket_id, staff_user_id):
    result = ticketscollection.update_one({"_id": ticket_id, "claimed_by": None}, {"$set": {"claimed_by": staff_user_id}})
    return result.modified_count

def mongo_unclaim_ticket(ticket_id, staff_user_id):
    # Only the current claimer (or if we wanted: allow any staff) can unclaim; enforce match
    result = ticketscollection.update_one({"_id": ticket_id, "claimed_by": staff_user_id}, {"$set": {"claimed_by": None}})
    return result.modified_count

def mongo_get_ticket_id(channel_id):
    ticket = ticketscollection.find_one({"channel_id": channel_id})
    return ticket["_id"] if ticket else None

def mongo_delete_ticket(ticket_id):
    result = ticketscollection.delete_one({"_id": ticket_id})
    return result.deleted_count

def mongo_ticket_channel_exists(channel_id):
    ticket = ticketscollection.find_one({"channel_id": channel_id})
    return ticket is not None
