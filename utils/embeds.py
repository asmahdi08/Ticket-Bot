import discord

def create_ticket_embed(ticket_id, creator_user, channel):
    embed = discord.Embed(
        title="Welcome to your Ticket",
        description=f"Ticket ID: {ticket_id}\n"
                    f"Creator: {creator_user.mention}\n"
                    f"**A support staff will reach you at any moment.**",
        color=discord.Color.green()
    )
    embed.set_footer(text="Use /ticket close to close this ticket.")
    return embed

def close_ticket_embed(ticket_id, creator_user):
    embed = discord.Embed(
        title="Ticket Closed",
        description=f"Ticket ID: {ticket_id}\n"
                    f"Creator: {creator_user.mention}\n"
                    f"**Thank you for using our support system!**",
        color=discord.Color.red()
    )
    embed.set_footer(text="If you need further assistance, feel free to open a new ticket.")
    return embed

def claim_ticket_embed(ticket_id, claimer: discord.Member):
    embed = discord.Embed(
        title="Ticket Claimed",
        description=f"This ticket has been claimed by: {claimer.mention}",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Support staff is now handling this ticket.")
    return embed