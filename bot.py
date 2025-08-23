import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import signal
import sys
from ui.TicketSetupView import TicketSetupView

LOG_LEVEL = logging.DEBUG if os.getenv("DEBUG") == "1" else logging.INFO
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger("keepalivebot")


intents = discord.Intents.default()

intents.message_content = True

load_dotenv()

required_env = ["BOT_TOKEN", "GUILD_ID", "SUPPORT_ROLE_ID", "DB_TYPE"]
missing = [k for k in required_env if not os.getenv(k)]
if missing:
    logger.error("Missing required environment variables: %s", ", ".join(missing))
    sys.exit(1)

BOT_TOKEN = os.getenv("BOT_TOKEN")
try:
    GUILD_ID = int(os.getenv("GUILD_ID"))
except (TypeError, ValueError):
    logger.error("GUILD_ID must be an integer")
    sys.exit(1)
GUILD_OBJ = discord.Object(GUILD_ID)
SUPPORT_ROLE_ID = int(os.getenv("SUPPORT_ROLE_ID"))
DB_TYPE = os.getenv("DB_TYPE")

bot = commands.Bot(command_prefix="!", intents=intents)
bot.synced_once = False

@bot.event
async def on_ready():
    logger.info("Logged in as %s (%s)", bot.user, bot.application.id if bot.application else "?")
    bot.add_view(TicketSetupView())
    logger.info("Persistent view registered")
    # Load cog if not loaded
    if "cogs.TicketCog" not in bot.extensions:
        await bot.load_extension("cogs.TicketCog")
        logger.info("TicketCog loaded")
    if not bot.synced_once:
        try:
            cmds = await bot.tree.sync(guild=GUILD_OBJ)
            logger.info("Synced %d commands to guild %s", len(cmds), GUILD_ID)
        except Exception as e:
            logger.warning("Command sync skipped/failed: %s", e)
        bot.synced_once = True

def _graceful_shutdown(*_):
    logger.info("Shutting down...")
    try:
        if DB_TYPE == "sqlite":
            from db.sqllite import sqlite_close
            sqlite_close()
        elif DB_TYPE == "mysql":
            from db.mysql import mysql_close
            mysql_close()
    except Exception as e:
        logger.debug("Error during DB close: %s", e)
    finally:
        sys.exit(0)

signal.signal(signal.SIGINT, _graceful_shutdown)
signal.signal(signal.SIGTERM, _graceful_shutdown)



bot.run(token=BOT_TOKEN)