from os import listdir
from os import rename
from traceback import format_exc

from discord import Forbidden
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.app_commands import CheckFailure
from discord.app_commands import CommandInvokeError
from discord.app_commands import CommandOnCooldown
from discord.ext.commands import Cog
from discord.ext.tasks import loop

from logging import getLogger

logger = getLogger(__name__)


async def on_error(interaction: Interaction, err: AppCommandError):

    ping = interaction.user.mention
    reply = interaction.response.send_message

    if isinstance(err, CommandOnCooldown):
        await reply(f"{ping}, you are on cooldown. Try again in {round(err.retry_after, 2)}s.")

    elif isinstance(err, CheckFailure):
        await reply(f"{ping}, missing permissions to run this command.")

    elif isinstance(err, CommandInvokeError):

        if isinstance(err.original, Forbidden):
            pass

        else:
            await reply(f"{ping}, something went wrong.")
            print(format_exc())

    else:
        await reply(f"{ping}, something went wrong.")
        print(format_exc())


async def setup(bot):
    await bot.add_cog(Event(bot))


class Event(Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.tree.on_error = on_error

    @loop(hours=24)
    async def log_file_fix(self):

        for file in listdir("data/logs"):
            if file == "active_log.txt" or file.startswith("log_"):
                return
            rename(f"data/logs/{file}", f"data/logs/log_{file[15:]}.txt")
