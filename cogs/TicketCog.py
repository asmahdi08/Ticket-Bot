import discord
from discord import app_commands
from discord.ext import commands
import logging
import os
from utils.botutils import (
    add_to_ticket,
    create_ticket,
    close_ticket,
    delete_ticket,
    remove_from_ticket,
    claim_ticket,
    unclaim_ticket,
)
from db.db_interface import db_ticket_channel_exists, db_get_ticket, db_get_ticket_id
from ui.TicketSetupView import TicketSetupView

logger = logging.getLogger("keepalivebot.ticketcog")

GUILD_ID = int(os.getenv("GUILD_ID"))
SUPPORT_ROLE_ID = int(os.getenv("SUPPORT_ROLE_ID"))


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ticket = app_commands.Group(name="ticket", description="Ticket management commands", guild_ids=[GUILD_ID])
    
    
    @ticket.command(name="setup", description="Setup ticket panel embed")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def setup_ticket_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description=(
                "Need help? Click the button below to open a ticket.\n\n"
                "**Our team will assist you as soon as possible.**"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Support System")

        view = TicketSetupView()

        await interaction.response.send_message(embed=embed, view=view)

    @ticket.command(name="create", description="Create a new ticket")
    async def create_ticket_command(self, interaction: discord.Interaction):
        try:
            ticket_id = await create_ticket(interaction.guild, interaction.user, SUPPORT_ROLE_ID)
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}")
            await interaction.response.send_message("Failed to create ticket.", ephemeral=True)
            return
        if ticket_id is None:
            await interaction.response.send_message("Ticket creation failed (support role missing or channel error).", ephemeral=True)
            return
        await interaction.response.send_message(f"Ticket created! ID: {ticket_id[:8]} (check the new channel).", ephemeral=True)

    @ticket.command(name="close", description="Close an existing ticket")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def close_ticket_commands(self, interaction: discord.Interaction):
        if not db_ticket_channel_exists(interaction.channel.id):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return
        try:
            await close_ticket(interaction.channel, interaction.guild, SUPPORT_ROLE_ID, interaction.user)
        except Exception as e:
            logger.error(f"Failed to close ticket: {e}")
            await interaction.response.send_message("Failed to close ticket.", ephemeral=True)
            return

        await interaction.response.send_message("Ticket closed!", ephemeral=True)
        
    @ticket.command(name="delete", description="Delete a ticket")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def delete_ticket_command(self, interaction: discord.Interaction):
        if not db_ticket_channel_exists(interaction.channel.id):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return
        # Send the ephemeral response BEFORE deleting the channel, otherwise 10003 Unknown Channel
        await interaction.response.send_message("Ticket deleted!", ephemeral=True)
        try:
            await delete_ticket(interaction.channel)
        except discord.NotFound:
            logger.warning("Channel already gone while deleting ticket.")

    @ticket.command(name="add", description="Add a user to a ticket")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def add_to_ticket_command(self, interaction: discord.Interaction, user: discord.User):
        if not db_ticket_channel_exists(interaction.channel.id):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return
        try:
            await add_to_ticket(interaction.channel, user)
        except Exception as e:
            logger.error(f"Failed to add user to ticket: {e}")
            await interaction.response.send_message("Failed to add user to ticket.", ephemeral=True)
            return

        await interaction.response.send_message("User added to ticket!", ephemeral=True)
        
    @ticket.command(name="remove", description="Remove a user from a ticket")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def remove_from_ticket_command(self, interaction: discord.Interaction, user: discord.User):
        if not db_ticket_channel_exists(interaction.channel.id):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return
        try:
            await remove_from_ticket(interaction.channel, user)
        except Exception as e:
            logger.error(f"Failed to remove user from ticket: {e}")
            await interaction.response.send_message("Failed to remove user from ticket.", ephemeral=True)
            return

        await interaction.response.send_message("User removed from ticket!", ephemeral=True)

    @ticket.command(name="claim", description="Claim a ticket")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def claim_ticket_command(self, interaction: discord.Interaction):
        # Optional: ensure user has support role
        if SUPPORT_ROLE_ID not in [r.id for r in getattr(interaction.user, 'roles', [])]:
            await interaction.response.send_message("You don't have permission to claim tickets.", ephemeral=True)
            return
        if not db_ticket_channel_exists(interaction.channel.id):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return
        try:
            result = await claim_ticket(interaction.channel, interaction.user)
        except Exception as e:
            logger.error(f"Failed to claim ticket: {e}")
            await interaction.response.send_message("Failed to claim ticket.", ephemeral=True)
            return

        if result == "success":
            await interaction.response.send_message("Ticket claimed!", ephemeral=True)
        elif result == "already_claimed":
            ticket_id = db_get_ticket_id(interaction.channel.id)
            ticket = db_get_ticket(ticket_id) if ticket_id else None
            claimer = ticket.get("claimed_by") if ticket and ticket.get("claimed_by") else None
            await interaction.response.send_message(f"Ticket already claimed by <@{claimer}>." if claimer else "Ticket already claimed.", ephemeral=True)
        else:
            await interaction.response.send_message("Unable to claim ticket (not found or unexpected error).", ephemeral=True)

    @ticket.command(name="unclaim", description="Unclaim a ticket you have claimed")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def unclaim_ticket_command(self, interaction: discord.Interaction):
        if not db_ticket_channel_exists(interaction.channel.id):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return
        try:
            unclaimed = await unclaim_ticket(interaction.channel, interaction.user)
        except Exception as e:
            logger.error(f"Failed to unclaim ticket: {e}")
            await interaction.response.send_message("Failed to unclaim ticket.", ephemeral=True)
            return
        if unclaimed == "success":
            await interaction.response.send_message("Ticket unclaimed.", ephemeral=True)
        else:
            await interaction.response.send_message("You haven't claimed this ticket or it's not claimed.", ephemeral=True)

    @ticket.command(name="info", description="Show information about this ticket")
    @app_commands.checks.has_role(SUPPORT_ROLE_ID)
    async def ticket_info(self, interaction: discord.Interaction):
        if not db_ticket_channel_exists(interaction.channel.id):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return
        # Fetch ticket record
        from db.db_interface import db_get_ticket_id as _get_tid
        ticket_id = _get_tid(interaction.channel.id)
        from db.db_interface import db_get_ticket as _get_ticket
        rec = _get_ticket(ticket_id)
        if not rec:
            await interaction.response.send_message("Ticket record not found.", ephemeral=True)
            return
        desc = [
            f"ID: {rec.get('id') or rec.get('_id')}",
            f"Status: {rec.get('status')}",
            f"Creator: <@{rec.get('creator_id')}>" if rec.get('creator_id') else "Creator: ?",
            f"Claimed By: <@{rec.get('claimed_by')}>" if rec.get('claimed_by') else "Claimed By: (unclaimed)",
        ]
        await interaction.response.send_message("\n".join(desc), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
    