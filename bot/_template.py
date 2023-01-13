from logging import getLogger

from discord import Interaction
from discord.app_commands import command
from discord.ext.commands import Cog

from utils.logger import get_log_decorator

log_as = get_log_decorator(getLogger(__name__))


async def setup(bot):
    await bot.add_cog(Template(bot))


class Template(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name="test")
    @log_as("/test")
    async def test(self, interaction: Interaction):

        pass
