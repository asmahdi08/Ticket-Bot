import discord
from utils.botutils import create_ticket
import os

support_role_id = int(os.getenv("SUPPORT_ROLE_ID"))

class TicketSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # no timeout so it stays persistent

    @discord.ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction.guild, interaction.user, support_role_id)
        await interaction.response.send_message(f"Ticket created!", ephemeral=True)

