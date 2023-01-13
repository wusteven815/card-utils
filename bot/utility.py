from logging import getLogger
from re import MULTILINE
from re import compile
from re import findall
from re import sub
from typing import Callable

from discord import Interaction
from discord import Message
from discord import SelectOption
from discord.app_commands import ContextMenu
from discord.ext.commands import Bot
from discord.ext.commands import Cog
from discord.ui import Select
from discord.ui import View

from utils.checks import is_card_embed
from utils.db import read_json
from utils.logger import get_log_decorator

log_as = get_log_decorator(getLogger(__name__))


class GetCleanAdSelect(Select):

    def __init__(self, author_id, clean_series):

        super().__init__(
            placeholder="More cleaning options...",
            min_values=1, max_values=3,
            options=[
                SelectOption(
                    label="Remove infrequently used properties",
                    description="Removes wishlist, effort, and quality columns.",
                    emoji="✂"),
                SelectOption(
                    label="Clean series names",
                    description="Shortens long names and removes season count.",
                    emoji="✂"),
                SelectOption(
                    label="Add ticket emoji",
                    description="Adds a ticket emoji before each line.",
                    emoji="🎟"),
                SelectOption(
                    label="Add gem emoji",
                    description="Adds a gem emoji before eacb line.",
                    emoji="💎")])

        self.author_id = author_id
        self.clean_series = clean_series

    async def callback(self, interaction: Interaction):

        if interaction.user.id != self.author_id:
            await interaction.response.defer()
            return

        new_msg = interaction.message.content

        if "Remove infrequently used properties" in self.values:
            # Remove wishlist
            new_msg = sub(r" · \\``♡([\d ]{1,5})`\\`", "", new_msg)
            # Remove effort
            new_msg = sub(r" · \\``✧([\d ]{1,3})`\\`", "", new_msg)
            # Remove effort
            new_msg = sub(r" · ([★☆]{4})", "", new_msg)

        if "Clean series names" in self.values:
            for series in findall(compile(r".*· (.*)$", MULTILINE), new_msg):
                if series in self.clean_series:
                    new_msg = new_msg.replace(series, self.clean_series[series])

        if "Add ticket emoji" in self.values:
            new_msg = sub(compile(r"^(.*)", MULTILINE), r"🎟 \1", new_msg)

        if "Add gem emoji" in self.values:
            new_msg = sub(compile(r"^(.*)", MULTILINE), r"💎 \1", new_msg)

        await interaction.message.edit(content=new_msg + "__\n__", view=None)
        await interaction.response.defer()


class GetCleanAdView(View):
    def __init__(self, author_id, clean_series):
        super().__init__(timeout=30)
        self.add_item(GetCleanAdSelect(author_id, clean_series))


async def get_main(interaction: Interaction, message: Message, collection_parser: Callable, view=None):

    reply = interaction.response.send_message
    error_msg = "Message must be a card collection."

    # Errors
    if not is_card_embed("Card Collection", message):
        await reply(error_msg, ephemeral=True)
    elif message.embeds[0].description[-18:] == "The list is empty.":
        await reply(error_msg, ephemeral=True)

    # Send result
    else:
        if view is None:
            await reply(collection_parser(message.embeds[0].description[40:]))
        else:
            await reply(collection_parser(message.embeds[0].description[40:]), view=view)


async def setup(bot: Bot):
    await bot.add_cog(Utility(bot))


class Utility(Cog):

    def __init__(self, bot):

        self.bot = bot
        self.context_menus_raw = {
            "Get Code": self.get_code,
            "Get Clean Ad": self.get_clean_ad}
        self.context_menus = []

        for name, func in self.context_menus_raw.items():
            context_menu = ContextMenu(
                name=name,
                callback=func)
            self.bot.tree.add_command(context_menu)
            self.context_menus.append(context_menu)

        self.clean_series = read_json("clean_series")

    async def cog_unload(self) -> None:
        for context_menu in self.context_menus:
            self.bot.tree.remove_command(context_menu.name, type=context_menu.type)

    @log_as("Get Clean Ad")
    async def get_clean_ad(self, interaction: Interaction, message: Message):

        await get_main(
            interaction, message,
            # First sub formats it, 2nd sub adds block code formatting
            lambda collection: sub(r"`(.+?)`", r"\\``\1`\\`", sub(r"(.*?) (`♡[\d ]{1,5}`)?( · )?(`✧[\d ]{1,3}`)?( · )?\*\*(.+?)\*\* · `([★☆]{4})` · `(.+?)` · `◈(\d)` · (.+?) · \*\*(.+?)\*\*", r"\6 · \2\3\4\5\7 · `◈\9 \8` · \\*\\***\g<11>**\\*\\* · \g<10>", collection)),
            view=GetCleanAdView(interaction.user.id, self.clean_series))

    @log_as("Get Code")
    async def get_code(self, interaction: Interaction, message: Message):

        await get_main(
            interaction, message,
            lambda collection: ", ".join(findall(r"\*\*`(.{3,6})`\*\*", collection)))
