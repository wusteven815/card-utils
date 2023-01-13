from logging import getLogger
from typing import Optional

from discord import Colour
from discord import Embed
from discord import Interaction
from discord.app_commands import Choice
from discord.app_commands import Group
from discord.app_commands import choices
from discord.app_commands import command
from discord.app_commands import describe
from discord.app_commands import rename
from discord.ext.commands import Cog
from discord.ui import View
from discord.ui import button

from utils.logger import get_log_decorator

log_as = get_log_decorator(getLogger(__name__))


async def setup(bot):
    await bot.add_cog(Info(bot))


class Info(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name="help", description="Get help on a command or list all commands")
    @rename(option="command")
    @describe(option="A command to search get help on")
    @log_as("/help")
    async def help(self, interaction: Interaction, option: Optional[str]):

        match ("None" if option is None else option.lower()):

            # Clan

            case "clan info":
                embed = Embed(
                    title="Help: `/clan info`",
                    description="Shows info on the clan verification system in this server.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            case "clan delete":
                embed = Embed(
                    title="Help: `/clan delete`",
                    description="Deletes the clan verification system in this server. Only users with the `Manage "
                                "server` permission can use this command.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            case "clan setup":
                embed = Embed(
                    title="Help: `/clan verify`",
                    description="**Options:**\n`shogun` - The shogun of this server\n`general_role` - The role given "
                                "to all members, regardless of rank (optional)\n`tairo_role` - The role given to only "
                                "Tairos (optional)\n`roju_role` - The role given to only Rojus ("
                                "optional)\n`ometsuke_role` - The role given to only Ometsukes ("
                                "optional)\n`daimyo_role` - The role given to only Daimyo (optional)\n`gundai_role` - "
                                "The role given to only Gundai (optional)\n`monogashiro_role` - The role given to "
                                "only Monogashiro (optional)\n`ashigaru_role` - The role given to only Ashigaru ("
                                "optional)\n`chonin_role` - The role given to only Chonin (optional)\n\nSets up the "
                                "clan verification system for this server. Only those with the `Manage server` "
                                "permission can use this command. ",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            case "clan verify":
                embed = Embed(
                    title="Help: `/clan verify`",
                    description="Verifies if you are in the clan of this server. If so, adds the appropriate roles.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            # Frame

            case "frame shop":
                embed = Embed(
                    title="Help: `/frame shop`",
                    description="**Options:**\n`tags` - These are tags you want to start off with",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            case "frame tags":
                embed = Embed(
                    title="Help: `/frame tags`",
                    description="Returns a list of all the tags used in frame related commands.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            case "test frames on" | "frame test":
                embed = Embed(
                    title="Help: `Test Frames On`",
                    description="⚠ This context menu can only be used on card messages.\n\nFrame "
                                "test lets you test a frame on a character without owning the frame. This command can "
                                "text at most 10 frames at the same time. If more than 10 frames exist in a tag, then "
                                "the first 10 alphabetically will be tested.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a context menu. To learn more, do /new_comands.")

            # Info

            case "help":
                embed = Embed(
                    title="Help: `/help`",
                    description="**Options:**\n`command` - Command to get help on (optional)\n\nReturns a guide on "
                                "how to use a command if one is specified. Otherwise returns a list of all commands.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            case "link":
                embed = Embed(
                    title="Help: `/link`",
                    description="**Options:**\n`option` - Name of the link to get",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            case "new commands":
                embed = Embed(
                    title="Help: `/new commands`",
                    description="Returns a guide on Discord's new command system.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a slash command. To learn more, do /new commands.")

            # Utility

            case "get code":
                embed = Embed(
                    title="Help: `Get Code`",
                    description="⚠ This context menu can only be used on collection messages.\n\nReturns a list "
                                "of all the codes in the collection. The list is compatible with commands like "
                                "`k!tag`, `k!burn`, and `k!multitrade`.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a context menu. To learn more, do /new_comands.")

            case "get clean ad":
                embed = Embed(
                    title="Help: `Get Clean Ad`",
                    description="⚠ This context menu can only be used on collection messages.\n\nReturns an "
                                "organized, copy-paste friendly ad of the collection. You can further customize the ad "
                                "and/or save character space in the dropdown.",
                    colour=Colour.light_grey())
                embed.set_footer(text="This is a context menu. To learn more, do /new_comands.")

            # Other

            case "None":
                embed = Embed(
                    title="Commands",
                    description="Slash commands are entries that start with a \"/\". Context menus are entries that do "
                                "not. To learn more, do `/new_commands`.",
                    colour=Colour.light_grey())
                embed.add_field(
                    name="Clan",
                    value="`/clan info`\n`/clan delete`\n`/clan setup`\n`/clan verify`")
                embed.add_field(
                    name="Frame",
                    value="`/frame shop`\n`/frame tags`\n`Test Frames On`")
                embed.add_field(
                    name="Info",
                    value="\n`/help`\n`/link`\n`/new commands`")
                embed.add_field(
                    name="Utility",
                    value="`Get Code`\n`Get Clean Ad`")

            case option:
                await interaction.response.send_message(f"No command found named `{option}`.", ephemeral=True)
                return

        await interaction.response.send_message(f"{interaction.user.mention}", embed=embed)

    @help.autocomplete("option")
    async def help_autocomplete_option(self, _, current: str):

        items = ("clan info", "clan delete", "clan setup", "clan verify",
            
                 "frame shop", "frame tags", "Test Frames On", "frame test",

                 "link", "help", "new commands",

                 "Get Code", "Get Clean Ad")
        return [Choice(name=item, value=item) for item in items if current.lower() in item.lower()]

    @command(name="link", description="Get links to useful resources.")
    @rename(key="option")
    @choices(key=[
        Choice(name="Date Sheet", value="date_sheet"),
        Choice(name="Trello", value="trello")])
    @log_as("/link")
    async def link(self, interaction: Interaction, key: Choice[str]):

        match key.value:

            case "date_sheet":
                await interaction.response.send_message(
                    interaction.user.mention +
                    ", https://docs.google.com/spreadsheets/d/10xBulRf2GrUEGRngokwTxoIYNEzbS03ZX5Ka6UWdINk/edit?usp=s" +
                    "haring")

            case "trello":
                await interaction.response.send_message(
                    f"{interaction.user.mention}")

    new = Group(name="new", description="...")

    @new.command(name="commands", description="A guide to help users learn about Discord' new command system")
    @log_as("/new commands")
    async def new_commands(self, interaction: Interaction):

        sc_embed = Embed(title="Slash Commands", colour=Colour.light_grey())
        sc_embed.add_field(
            name="For users",
            value="It's as simple as pressing / and you'll see all the available commands, as well as all the bots "
                  "that have usable commands in the channel.\n\n_ _",
            inline=False)
        sc_embed.add_field(
            name="For server admins",
            value="Server admins can change who can use which chnnels in the Integration section in server settings. "
                  "If you click on each command, you can further customize permissions.\n\nFor a more in-depth "
                  "explaination, I recommend reading [this blog post by Discord]("
                  "https://discord.com/blog/slash-commands-permissions-discord-apps-bots).",
            inline=False)

        cm_embed = Embed(title="Context Menus", colour=Colour.light_grey())
        cm_embed.add_field(
            name="For users",
            value="There are 2 types of context menus: message and user. When you right click a message or user, "
                  "if there are any context menus registered, a selection called Apps shows you all the context menus "
                  "usable in the channel",
            inline=False)
        cm_embed.add_field(
            name="For server admins",
            value="Server admins can change who can use which chnnels in the Integration section in server settings. "
                  "If you click on each command, you can further customize permissions.\n\nFor a more in-depth "
                  "explaination, I recommend reading [this blog post by Discord]("
                  "https://discord.com/blog/slash-commands-permissions-discord-apps-bots) (yes, I know it says slash "
                  "commands but the permission guide applys to context menus).",
            inline=False)

        class NewCommandsView(View):

            def __init__(self):
                super().__init__(timeout=30)

            @button(label="Slash Commands")
            async def button_sc(self, interaction_: Interaction, _):
                await interaction_.response.edit_message(embed=sc_embed)

            @button(label="Context Menus")
            async def button_cm(self, interaction_: Interaction, _):
                await interaction_.response.edit_message(embed=cm_embed)

        await interaction.response.send_message(interaction.user.mention, embed=sc_embed, view=NewCommandsView())
