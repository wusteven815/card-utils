from logging import getLogger

from discord import Embed
from discord import Interaction
from discord.app_commands import Group
from discord.app_commands import check
from discord.app_commands import command
from discord.app_commands import describe
from discord.ext.commands import Cog

from env import guild
from utils.checks import cog_check_admin
from utils.db import aread_json
from utils.db import awrite_json
from utils.logger import get_log_decorator

log_as = get_log_decorator(getLogger(__name__))
utility_cog = "Utility"


async def setup(bot):
    await bot.add_cog(Admin(bot))


class Admin(Cog):

    def __init__(self, bot):
        self.bot = bot

    clean = Group(name="clean", description="...", guild_only=True, guild_ids=[guild.id])
    clean_series = Group(name="series", description="...", parent=clean)

    @clean_series.command(name="add", description="Add to clean series list")
    @describe(before="Series to replace", after="Series replaced with")
    @check(cog_check_admin)
    @log_as("/clean series add")
    async def clean_series_add(self, interaction: Interaction, before: str, after: str):

        clean_series = self.bot.cogs[utility_cog].clean_series

        clean_series[before] = after
        await awrite_json("clean_series", clean_series, sort=True)
        await interaction.response.send_message(
            f"{interaction.user.mention}, successfully added:\n" +
            f"**Before:** `{before}`\n" +
            f"**After:** `{after}`")

    @clean_series.command(name="refresh", description="Refresh clean series list")
    @check(cog_check_admin)
    @log_as("/clean series refresh")
    async def clean_series_refresh(self, interaction: Interaction):

        self.bot.cogs[utility_cog].clean_series = await aread_json("clean_series")
        await interaction.response.send_message(f"{interaction.user.mention}, successfully refreshed.")

    @clean_series.command(name="delete", description="Delete clean series list")
    @describe(series="Series to delete")
    @check(cog_check_admin)
    @log_as("/clean series delete")
    async def clean_series_delete(self, interaction: Interaction, series: str):

        clean_series = self.bot.cogs[utility_cog].clean_series
        ping = interaction.user.mention
        reply = interaction.response.send_message

        try:
            clean_series.pop(series)

        except KeyError:
            await reply(f"{ping}, no series found named `{series}`.")

        else:
            await awrite_json("clean_series", clean_series)
            await reply(f"{ping}, successfully deleted `{series}`.")

    @command(name="info", description="General info about the bot")
    @check(cog_check_admin)
    @log_as("/info")
    async def info(self, interaction: Interaction):

        await interaction.response.send_message(
            embed=Embed(
                title="Bot Info",
                description=f"**Username:** {self.bot.user}\n**User ID:** {self.bot.user.id}\n**Guild Count**: " +
                            f"{len(self.bot.guilds)}",),
            ephemeral=True)
