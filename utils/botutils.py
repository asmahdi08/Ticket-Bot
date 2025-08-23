from db.db_interface import (
    db_create_ticket,
    db_close_ticket,
    db_get_ticket,
    db_update_ticket_status,
    db_update_ticket_channel,
    db_get_ticket_id,
    db_delete_ticket,
    db_ticket_channel_exists,
    db_claim_ticket,
    db_unclaim_ticket,
)
from utils.embeds import create_ticket_embed, close_ticket_embed, claim_ticket_embed
import discord
import logging

logger = logging.getLogger("keepalivebot.utils.botutils")


async def create_ticket(guild: discord.Guild, creator_user, support_role_id):
    """Create a ticket channel and DB record.

    Returns the ticket_id on success, or None on failure.
    """
    ticket_id = db_create_ticket(guild.id, None, creator_user.id)
    support_role = guild.get_role(support_role_id)
    if support_role is None:
        logger.error("Support role with id %s not found; aborting ticket creation", support_role_id)
        return None

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        creator_user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    try:
        channel = await guild.create_text_channel(
            f"ticket-{ticket_id[:8]}", overwrites=overwrites
        )
    except discord.Forbidden:
        logger.error("Failed to create ticket channel due to permissions error.")
        return None
    except Exception as e:
        logger.error("Failed to create ticket channel: %s", e)
        return None

    db_update_ticket_channel(ticket_id, channel.id)
    logger.info("Created ticket %s in channel %s", ticket_id, channel.id)

    embed = create_ticket_embed(ticket_id, creator_user, channel)
    await channel.send(embed=embed)
    return ticket_id
    
async def delete_ticket(channel):
    if db_ticket_channel_exists(channel.id):
        ticket_id = db_get_ticket_id(channel.id)
        await channel.delete()
        db_delete_ticket(ticket_id)
        logger.info(f"Deleted ticket {ticket_id}")

async def close_ticket(channel:discord.TextChannel, guild:discord.Guild, support_role_id, creator_user):
    if db_ticket_channel_exists(channel.id):
        ticket_id = db_get_ticket_id(channel.id)
        db_close_ticket(ticket_id)
        
        support_role = guild.get_role(support_role_id)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            creator_user: discord.PermissionOverwrite(read_messages=True, send_messages=False)
        }

        await channel.edit(overwrites=overwrites)

        embed = close_ticket_embed(ticket_id, creator_user)

        await channel.send(embed=embed)
        logger.info(f"Closed ticket {ticket_id}")

async def add_to_ticket(channel: discord.TextChannel, user: discord.User):
    if db_ticket_channel_exists(channel.id):
        ticket_id = db_get_ticket_id(channel.id)
        # db_add_user_to_ticket(ticket_id, user.id)
        
        overwrites = channel.overwrites
        
        overwrites[user] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        await channel.edit(overwrites=overwrites)
        
        
        logger.info(f"Added user {user.id} to ticket {ticket_id}")

async def remove_from_ticket(channel: discord.TextChannel, user: discord.User):
    if db_ticket_channel_exists(channel.id):
        ticket_id = db_get_ticket_id(channel.id)
        # db_remove_user_from_ticket(ticket_id, user.id)

        overwrites = channel.overwrites

        if user in overwrites:
            del overwrites[user]
            await channel.edit(overwrites=overwrites)

        logger.info(f"Removed user {user.id} from ticket {ticket_id}")

async def claim_ticket(channel: discord.TextChannel, staff_member: discord.Member):
    if not db_ticket_channel_exists(channel.id):
        return "error"
    ticket_id = db_get_ticket_id(channel.id)
    modified = db_claim_ticket(ticket_id, staff_member.id)
    logger.debug("Claim attempt ticket_id=%s staff=%s rowcount=%s", ticket_id, staff_member.id, modified)
    if modified:
        embed = claim_ticket_embed(ticket_id, staff_member)
        await channel.send(embed=embed)
        return "success"
    # No row modified: either already claimed or missing. Fetch for clarity.
    ticket_record = db_get_ticket(ticket_id)
    logger.debug("Post-claim fetch ticket_id=%s record=%s", ticket_id, ticket_record)
    if ticket_record and ticket_record.get("claimed_by") and ticket_record.get("claimed_by") != staff_member.id:
        return "already_claimed"
    if not ticket_record:
        return "error"
    # If claimed_by is None still, then maybe race or backend issue.
    return "error"

async def unclaim_ticket(channel: discord.TextChannel, staff_member: discord.Member):
    if not db_ticket_channel_exists(channel.id):
        return "error"
    ticket_id = db_get_ticket_id(channel.id)
    modified = db_unclaim_ticket(ticket_id, staff_member.id)
    if modified:
        await channel.send(f"Ticket unclaimed by {staff_member.mention}")
        return "success"
    return "error"
