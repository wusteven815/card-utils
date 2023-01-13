from logging import getLogger
from pathlib import Path

from discord import Interaction
from discord.app_commands import check
from discord.app_commands import command
from discord.app_commands import guilds
from discord.ext.commands import Cog

from env import guild
from utils.checks import cog_check_admin
from utils.logger import get_log_decorator

logger = getLogger(__name__)
log_as = get_log_decorator(logger)


async def setup(bot):
    await bot.add_cog(LiveChange(bot))


class LiveChange(Cog):

    def __init__(self, bot):
        self.bot = bot

    async def reload_extensions(self):

        exts = []

        # Unload all commands
        for ext in tuple(self.bot.extensions):
            await self.bot.unload_extension(ext)

        # Load livechange first as priority
        await self.bot.load_extension("bot._extchange")
        logger.info("Reloaded extension bot._extchange")

        # Dynamically load commands
        for ext in Path("bot").glob("*.py"):
            ext = str(ext).replace("\\", ".").replace("/", ".")[:-3]
            if ext not in (f"bot.{file}" for file in self.bot.ignore_files):
                # Load ext
                await self.bot.load_extension(ext)
                logger.info(f"Reloaded extension {ext}")
                exts.append(ext)

        return "\n".join(f"> `{ext}`" for ext in exts)

    @command(name="reload", description="Reload all commands")
    @guilds(guild)
    @check(cog_check_admin)
    @log_as("/reload")
    async def reload(self, interaction: Interaction):

        exts = await self.reload_extensions()
        await interaction.response.send_message(
            f"{interaction.user.mention}, successfully reloaded all extensions:\n{exts}")

    @command(name="resync", description="Reload and resync all commands")
    @guilds(guild)
    @check(cog_check_admin)
    @log_as("/resync")
    async def resync(self, interaction: Interaction):

        exts = await self.reload_extensions()
        # Global commands, with admin guild commands
        if guild.id == 0:
            await self.bot.tree.sync()
            await self.bot.tree.sync(guild=guild)
            logger.info("Commands resynced to global scope")
        # Testing environment only
        elif guild.id == 0:
            self.bot.tree.copy_global_to(guild=guild)
            await self.bot.tree.sync(guild=guild)
            logger.info("Commands resynced to Pixell's Lab scope")

        await interaction.response.send_message(
            f"{interaction.user.mention}, successfully reloaded and resynced all extensions:\n{exts}")
