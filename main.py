from logging import INFO
from logging import StreamHandler
from logging import basicConfig as logging_basicConfig
from logging import getLogger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from sys import argv

from discord import Activity
from discord import ActivityType
from discord import Intents
from discord import Message
from discord import Status
from discord.ext.commands import Bot

from env import guild
from env import token

logging_basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format="{asctime} | {levelname: <8} | {name: <16} | {message}",
    handlers=[
        StreamHandler(),
        TimedRotatingFileHandler("data/logs/active_log.txt", utc=True, when="midnight", backupCount=14)],
    level=INFO,
    style="{")
logger = getLogger(__name__)


class CardUtils(Bot):

    def __init__(self):

        super().__init__(
            activity=Activity(
                name="",
                type=ActivityType.watching),
            command_prefix="",
            help_command=None,
            intents=Intents(
                guilds=True,
                guild_messages=True,
                message_content=True),
            status=Status.online)

        self.ignore_files = ["_extchange", "_template"]
        # Disable error checking on testing environment
        if guild.id == 0:
            self.ignore_files.append("event")

    async def setup_hook(self) -> None:

        # Load livechange first as priority
        await self.load_extension("bot._extchange")
        logger.info("Loaded extension bot._extchange")

        # Dynamically load commands
        for ext in Path("bot").glob("*.py"):
            ext = str(ext).replace("\\", ".").replace("/", ".")[:-3]
            if ext not in (f"bot.{file}" for file in self.ignore_files):
                # Load ext
                await self.load_extension(ext)
                logger.info(f"Loaded extension {ext}")

        if "-resync" in argv:
            # Global commands, with admin guild commands
            if guild.id == 0:
                await self.tree.sync()
                await self.tree.sync(guild=guild)
                logger.info("Commands resynced to global scope")
            # Testing environment only
            elif guild.id == 0:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info("Commands resynced to Pixell's Lab scope")

    async def on_message(self, message: Message, /) -> None:
        # Ignore all messages
        pass

    # TODO replace with proper setup
    async def on_ready(self) -> None:
        logger.info(f"Client connected to {bot.user}")


if guild.id in (0, 1):
    bot = CardUtils()
    bot.run(token, log_handler=None)
else:
    logger.warning("Invalid guild environmental veriable")
