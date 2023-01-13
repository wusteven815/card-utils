from asyncio import TimeoutError
from logging import getLogger
from re import fullmatch
from typing import Optional

from discord import Colour
from discord import Embed
from discord import Forbidden
from discord import HTTPException
from discord import Interaction
from discord import Message
from discord import NotFound
from discord import Role
from discord.app_commands import command
from discord.app_commands import describe
from discord.app_commands.checks import has_permissions
from discord.ext.commands import GroupCog
from discord.ext.tasks import loop
from discord.ui import View
from discord.ui import button

from utils.checks import is_card_embed
from utils.db import SQLite3
from utils.logger import get_log_decorator
from utils.views import ConfirmView

log_as = get_log_decorator(getLogger(__name__))


async def setup(bot):
    await bot.add_cog(Clan(bot))


class Clan(GroupCog, name="clan", description="Collection of commmands to help with clans"):

    def __init__(self, bot):

        self.bot = bot
        self.db = SQLite3()
        self.db_commit_task.start()

    async def cog_load(self):

        await self.db.connect("clanverify")
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS clanverify (
            id INTEGER PRIMARY KEY, 
            guild_id INTEGER,
            general_role_1 INTEGER,
            general_role_2 INTEGER,
            tairo_role INTEGER,
            roju_role INTEGER,
            ometsuke_role INTEGER,
            daimyo_role INTEGER,
            gundai_role INTEGER,
            monogashiro_role INTEGER,
            ashigaru_role INTEGER,
            chonin_role INTEGER)""")

    async def cog_unload(self):

        await self.db.close()

    @loop(seconds=0.05)
    async def db_commit_task(self):
        await self.db.commit()

    @command(name="info", description="Shows information about the clans in the server")
    @log_as("/clan info")
    async def clan_info(self, interaction: Interaction):

        ping = interaction.user.mention
        reply = interaction.response.send_message
        data = await self.db.execute(f"SELECT * FROM clanverify WHERE guild_id = {interaction.guild_id}", fetch="all")

        if len(data) == 0:
            await reply(ping, embed=Embed(
                title="Clan Verification Info",
                description="The clan verifcation system allows users to use the `/clan verify` command and get roles "
                            "related to the clan automatically.\n\nClan verification is **not set up** on this server."
                            "\n\nSee [here]"
                            "() for a "
                            "more detailed tutorial.",
                colour=Colour.light_grey()))

        else:

            index = 0
            clan_pages = [
                (
                    f"**Shogun:** <@{clan[0]}>\n**Server:** {interaction.guild.name}",
                    f"**General role 1:** {'<@&' + str(clan[2]) + '>' if clan[2] != 0 else 'Not set'}\n"
                    f"**General role 2:** {'<@&' + str(clan[3]) + '>' if clan[3] != 0 else 'Not set'}\n"
                    f"**Tairo role:** {'<@&' + str(clan[4]) + '>' if clan[4] != 0 else 'Not set'}\n"
                    f"**Roju role:** {'<@&' + str(clan[5]) + '>' if clan[5] != 0 else 'Not set'}\n"
                    f"**Ometsuke role:** {'<@&' + str(clan[6]) + '>' if clan[6] != 0 else 'Not set'}\n",
                    f"**Daimyo role:** {'<@&' + str(clan[7]) + '>' if clan[7] != 0 else 'Not set'}\n"
                    f"**Gundai role:** {'<@&' + str(clan[8]) + '>' if clan[8] != 0 else 'Not set'}\n"
                    f"**Monogashiro role:** {'<@&' + str(clan[9]) + '>' if clan[9] != 0 else 'Not set'}\n"
                    f"**Ashigaru role:** {'<@&' + str(clan[10]) + '>' if clan[10] != 0 else 'Not set'}\n"
                    f"**Chonin role:** {'<@&' + str(clan[11]) + '>' if clan[11] != 0 else 'Not set'}"
                ) for clan in data]
            cached_pfps = {}

            embed = Embed(
                title="Clan Verification Setup",
                description="The clan verification system allows users to use the `/clan verify` command and get roles "
                            "related to any clan setup in the server automatically.",
                colour=Colour.light_grey())
            embed.add_field(name="_ _", value=clan_pages[index][0], inline=False)
            embed.add_field(name="_ _", value=clan_pages[index][1])
            embed.add_field(name="_ _", value=clan_pages[index][2])
            embed.add_field(
                name="_ _",
                value="See [here]() "
                      "for a more detailed tutorial.",
                inline=False)
            embed.set_footer(text=f"Viewing clan {index + 1}/{len(clan_pages)}")

            shogun_id = data[index][0]
            try:
                shogun = await interaction.guild.fetch_member(shogun_id)
            except (Forbidden, HTTPException, NotFound):
                cached_pfps[shogun_id] = None
            else:
                embed.set_thumbnail(url=shogun.avatar.url)
                cached_pfps[shogun_id] = shogun.avatar.url

            async def _edit_embed(interaction_: Interaction):

                nonlocal embed, shogun_id

                embed.set_field_at(0, name="_ _", value=clan_pages[index][0], inline=False)
                embed.set_field_at(1, name="_ _", value=clan_pages[index][1])
                embed.set_field_at(2, name="_ _", value=clan_pages[index][2])
                embed.set_footer(text=f"Viewing clan {index + 1}/{len(clan_pages)}")

                shogun_id = data[index][0]
                # Access cache
                if shogun_id in cached_pfps:
                    if cached_pfps[shogun_id] is not None:
                        embed.set_thumbnail(url=cached_pfps[shogun_id])
                    else:
                        embed.set_thumbnail(url=None)
                # Cache
                else:
                    try:
                        shogun_ = await interaction.guild.fetch_member(shogun_id)
                    except (Forbidden, HTTPException, NotFound):
                        cached_pfps[shogun_id] = None
                        embed.set_thumbnail(url=None)
                    else:
                        embed.set_thumbnail(url=shogun_.avatar.url)
                        cached_pfps[shogun_id] = shogun_.avatar.url

                await interaction_.response.edit_message(embed=embed)

            class ClanInfoView(View):

                def __init__(self):
                    super().__init__(timeout=30)

                @button(emoji="◀")
                async def button_left(self, interaction_: Interaction, _):

                    nonlocal index
                    index = (index - 1) % len(clan_pages)
                    await _edit_embed(interaction_)

                @button(emoji="▶")
                async def button_right(self, interaction_: Interaction, _):

                    nonlocal index
                    index = (index + 1) % len(clan_pages)
                    await _edit_embed(interaction_)

            await reply(ping, embed=embed, view=ClanInfoView())

    @command(name="delete", description="Delete your clan for verification in this server")
    @has_permissions(manage_guild=True)
    @log_as("/clan delete")
    async def clan_delete(self, interaction: Interaction):

        ping = interaction.user.mention
        reply = interaction.response.send_message
        data = await self.db.get_key("clanverify", interaction.user.id)

        if data is None:
            await reply(f"{ping}, clan verification is not enabled for this server.")

        else:

            embed = Embed(title="Confirm", colour=Colour.yellow())
            view = ConfirmView()

            guild = self.bot.get_guild(data[1])
            if self.bot.get_guild(data[1]) is None:
                embed.description = "Are you sure you want to delete your clan's verification info?"
            else:
                embed.description = "Are you sure you want to delete your clan's verification info in " \
                                    f"**{guild.name}**?"

            await reply(ping, embed=embed, view=view)
            await view.wait()

            if view.confirmed is None:
                pass

            elif view.confirmed:
                await self.db.del_key("clanverify", interaction.user.id)
                embed.colour = Colour.green()
                await interaction.edit_original_message(embed=embed)

            else:
                embed.colour = Colour.red()
                await interaction.edit_original_message(embed=embed)

    @command(name="delete-force", description="Delete another user's clan for verification in this server")
    @has_permissions(manage_guild=True)
    @log_as("/clan delete-force")
    async def clan_delete_force(self, interaction: Interaction, shogun: str):

        reply = interaction.response.send_message
        ping = interaction.user.mention

        if fullmatch(r"\d{18,19}", shogun) is None:
            if "drop table" in shogun.lower():
                await reply(f"{ping}, invalid user ID lmao.")
            else:
                await reply(f"{ping}, invalid user ID.")
            return

        shogun = int(shogun)

        data = await self.db.execute(f"SELECT * FROM clanverify "
                                     f"WHERE id = {shogun} AND guild_id = {interaction.guild_id}", fetch="one")

        if data is None:
            await reply(f"{ping}, no clan registered in this server under shogun ID `{shogun}`.")

        else:

            embed = Embed(
                title="Confirm",
                description=f"Are you sure you want to delete <@{shogun}>'s clan's verification info?",
                colour=Colour.yellow())
            view = ConfirmView()

            await reply(ping, embed=embed, view=view)
            await view.wait()

            if view.confirmed is None:
                pass

            elif view.confirmed:
                await self.db.del_key("clanverify", shogun)
                embed.colour = Colour.green()
                await interaction.edit_original_message(embed=embed)

            else:
                embed.colour = Colour.red()
                await interaction.edit_original_message(embed=embed)

    @command(name="setup", description="Add your clan for verification in this server")
    @describe(general_role_1="First role to give to all verified members",
              general_role_2="Second role to give to all verified members",
              tairo_role="Role to give to Tairo level members",
              roju_role="Role to give to Roju level members",
              ometsuke_role="Role to give to Ometsuke level members",
              daimyo_role="Role to give to Daimyo level members",
              gundai_role="Role to give to Gundai level members",
              monogashiro_role="Role to give to Monogashiro level members",
              ashigaru_role="Role to give to Ashigaru level members",
              chonin_role="Role to give to Chonin level members")
    @has_permissions(manage_guild=True)
    @log_as("/clan setup")
    async def clan_setup(
            self,
            interaction: Interaction,
            general_role_1: Optional[Role],
            general_role_2: Optional[Role],
            tairo_role: Optional[Role],
            roju_role: Optional[Role],
            ometsuke_role: Optional[Role],
            daimyo_role: Optional[Role],
            gundai_role: Optional[Role],
            monogashiro_role: Optional[Role],
            ashigaru_role: Optional[Role],
            chonin_role: Optional[Role]
    ):

        reply = interaction.response.send_message
        ping = interaction.user.mention

        data = await self.db.get_key("clanverify", interaction.user.id)

        # Check is already have a clan verify in another server
        if data is not None:
            if data[1] != interaction.guild_id:
                last_guild = self.bot.get_guild(data[1])
                if last_guild is None:
                    await reply(f"{ping}, you already have a clan verification system in another server. If you want "
                                "to override that server, do `/clan delete` first.")
                else:
                    await reply(f"{ping}, you already have a clan verification system in another server "
                                f"(**{last_guild.name}**). If you want to override that server, do `/clan delete` "
                                "first.")
                return

        # Check if reached max server count
        data = await self.db.execute(f"SELECT * FROM clanverify WHERE guild_id = {interaction.guild_id}", fetch="all")
        for entry in data:
            if entry[0] == interaction.user.id:
                data.remove(entry)
                break

        # Set max guilds
        match interaction.guild_id:
            case _:
                max_clans = 8

        # Check if reached max server count part 2
        if len(data) >= max_clans:
            await reply(f"{ping}, this server has reached the maximum amount of clans of **{max_clans}**. If this "
                        "server needs more, please contact `PixellProton#8577`.")
            return

        # Check roles
        for role in (general_role_1, general_role_2, tairo_role, roju_role, ometsuke_role, daimyo_role, gundai_role,
                     monogashiro_role, ashigaru_role, chonin_role):
            if role is not None:
                if not role.is_assignable():
                    await reply(f"{ping}, the bot does not have the permissions to give the `{role.name}` role. " +
                                "Please make sure the bot has a role with the `Manage Roles` permission above the " +
                                f"`{role.name}` role.")
                    return

        # Add to database
        await self.db.set_key(
            "clanverify", interaction.user.id,
            guild_id=interaction.guild_id,
            general_role_1=general_role_1.id if general_role_1 is not None else 0,
            general_role_2=general_role_2.id if general_role_2 is not None else 0,
            tairo_role=tairo_role.id if tairo_role is not None else 0,
            roju_role=roju_role.id if roju_role is not None else 0,
            ometsuke_role=ometsuke_role.id if ometsuke_role is not None else 0,
            daimyo_role=daimyo_role.id if daimyo_role is not None else 0,
            gundai_role=gundai_role.id if gundai_role is not None else 0,
            monogashiro_role=monogashiro_role.id if monogashiro_role is not None else 0,
            ashigaru_role=ashigaru_role.id if ashigaru_role is not None else 0,
            chonin_role=chonin_role.id if chonin_role is not None else 0)

        # Send result
        embed = Embed(
            title="Clan Verification Setup",
            description="It's highly recommended to test out if the clan verification system works (fix any "
                        f"permission issues).",
            colour=Colour.green())
        embed.add_field(
            name="_ _",
            value=f"**Shogun:** {interaction.user.mention}\n**Server:** {interaction.guild.name}",
            inline=False)
        embed.add_field(
            name="_ _",
            value="**General role 1:** " +
                  ("<@&" + str(general_role_1.id) + ">" if general_role_1 is not None else "Not set") +
                  "\n**General role 2:** " +
                  ("<@&" + str(general_role_2.id) + ">" if general_role_2 is not None else "Not set") +
                  "\n**Tairo role:** " +
                  ("<@&" + str(tairo_role.id) + ">" if tairo_role is not None else "Not set") +
                  "\n**Roju role:** " +
                  ("<@&" + str(roju_role.id) + ">" if roju_role is not None else "Not set") +
                  "\n**Ometsuke role:** " +
                  ("<@&" + str(ometsuke_role.id) + ">" if ometsuke_role is not None else "Not set"))
        embed.add_field(
            name="_ _",
            value="\n**Daimyo role:** " +
                  ("<@&" + str(daimyo_role.id) + ">" if daimyo_role is not None else "Not set") +
                  "\n**Gundai role:** " +
                  ("<@&" + str(gundai_role.id) + ">" if gundai_role is not None else "Not set") +
                  "\n**Monogashiro role:** " +
                  ("<@&" + str(monogashiro_role.id) + ">" if monogashiro_role is not None else "Not set") +
                  "\n**Ashigaru role:** " +
                  ("<@&" + str(ashigaru_role.id) + ">" if ashigaru_role is not None else "Not set") +
                  "\n**Chonin role:** " +
                  ("<@&" + str(chonin_role.id) + ">" if chonin_role is not None else "Not set"))
        embed.add_field(
            name="_ _",
            value="See [here]() for a "
                  "more detailed tutorial.",
            inline=False)

        try:
            shogun = await interaction.guild.fetch_member(443197691267383310)
        except (Forbidden, HTTPException, NotFound):
            pass
        else:
            embed.set_thumbnail(url=shogun.avatar.url)

        await interaction.response.send_message(embed=embed)

    @command(name="verify", description="Verify that you are a member of this server's clan")
    @log_as("/clan verify")
    async def clan_verify(self, interaction: Interaction):

        ping = interaction.user.mention
        reply = interaction.response.send_message
        clans = await self.db.execute(f"SELECT * FROM clanverify WHERE guild_id = {interaction.guild_id}", fetch="all")

        if len(clans) is None:
            await reply(f"{ping}, there are no clans setup in this server.")

        else:

            clan = []

            await reply(f"{ping}, please do `k!clanview` (commonly `kcv`).")

            def message_check(message_: Message):
                if message_.channel.id == interaction.channel_id:
                    if is_card_embed("View Clan", message_):
                        return message_.embeds[0].description[27:45] == str(interaction.user.id)
                return False

            # Check for user's kcv message
            try:
                message = await self.bot.wait_for("message", timeout=30, check=message_check)
            except TimeoutError:
                return

            desc = message.embeds[0].description

            # Check clans
            found_clan = False
            for clan in clans:
                if desc.split("\n")[1][-30:-12] == str(clan[0]):
                    found_clan = True
                    break
            if not found_clan:
                await message.channel.send(f"{ping}, you are not in any of the clan(s) setup in this server.")
                return

            async def add_roles(rank_role_id: int, rank: str):

                desc = "Added the following roles:\n"

                for i in range(2):

                    general_role_id = clan[i + 2]

                    # Not set
                    if general_role_id == 0:
                        desc += f"\n**General role {i + 1}:** Not set"
                    else:
                        general_role = interaction.guild.get_role(general_role_id)
                        # Not found
                        if general_role is None:
                            desc += f"\n**General role {i + 1}:** Not found, please contact server admin"
                        else:
                            try:
                                await interaction.user.add_roles(general_role)
                            # No perm
                            except Forbidden:
                                desc += f"\n**General role {i + 1}:** Missing permissions, please contact "\
                                             "server admin"
                            # Success
                            else:
                                desc += f"\n**General role {i + 1}:** <@&{general_role_id}>"

                # Not set
                if rank_role_id == 0:
                    desc += f"\n> **{rank} role:** Not set"
                else:
                    rank_role = interaction.guild.get_role(rank_role_id)
                    # Not found
                    if rank_role is None:
                        desc += f"\n**{rank} role:** Not found, please contact server admin"
                    else:
                        try:
                            await interaction.user.add_roles(rank_role)
                        # No perm
                        except Forbidden:
                            desc += f"\n**{rank} role:** Missing permissions, please contact server admin"
                        # Success
                        else:
                            desc += f"\n**{rank} role:** <@&{rank_role_id}>"

                await message.channel.send(ping, embed=Embed(title="Verified", description=desc, colour=Colour.green()))

            match desc.split("\n")[1][4:-42]:

                case "Shogun":
                    await message.channel.send(f"{ping}, you're the shogun. No roles added.")
                case "Tairo":
                    await add_roles(clan[4], "Tairo")
                case "Roju":
                    await add_roles(clan[5], "Roju")
                case "Ometsuke":
                    await add_roles(clan[6], "Ometsuke")
                case "Daimyo":
                    await add_roles(clan[7], "Daimyo")
                case "Gundai":
                    await add_roles(clan[8], "Gundai")
                case "Monogashiro":
                    await add_roles(clan[9], "Monogashiro")
                case "Ashigaru":
                    await add_roles(clan[10], "Ashigaru")
                case "Chonin":
                    await add_roles(clan[11], "Chonin")
