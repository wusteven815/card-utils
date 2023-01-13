from asyncio import TimeoutError
from io import BytesIO
from logging import getLogger
from os import remove
from pathlib import Path
from string import capwords as title
from typing import Optional

from PIL import Image
from discord import Attachment
from discord import Colour
from discord import Embed
from discord import File
from discord import Interaction
from discord import Message
from discord.app_commands import ContextMenu
from discord.app_commands import check
from discord.app_commands import command
from discord.app_commands import describe
from discord.app_commands import guilds
from discord.app_commands import rename
from discord.app_commands.checks import cooldown
from discord.ext.commands import GroupCog
from discord.ui import View
from discord.ui import button
from requests import get

from env import guild
from utils.checks import cog_check_admin
from utils.checks import is_card_embed
from utils.db import awrite_json
from utils.db import read_json
from utils.logger import get_log_decorator

all_frames = read_json("frames")
log_as = get_log_decorator(getLogger(__name__))


def filter_frames(possible_tags: str, frames: list):

    # Loop through all frames
    new_frames = [frame for frame in frames if
                  # Check if all tag words in the tag phrase
                  all((word.lower() in frame["tags"]) for word in possible_tags.split())]

    # Invalid tag
    if len(new_frames) == 0:
        return False, frames

    return True, new_frames


async def setup(bot):
    await bot.add_cog(Frame(bot))


class Frame(GroupCog, name="frame", description="Collection of commmands to help with clans"):

    def __init__(self, bot):

        self.bot = bot
        self.context_menus_raw = {
            "Test Frames On": self.test_frames_on}
        self.context_menus = []

        for name, func in self.context_menus_raw.items():
            context_menu = ContextMenu(
                name=name,
                callback=func)
            self.bot.tree.add_command(context_menu)
            self.context_menus.append(context_menu)

        self.active_frametest = {}

    async def cog_unload(self) -> None:
        for context_menu in self.context_menus:
            self.bot.tree.remove_command(context_menu.name, type=context_menu.type)

    @command(name="add", description="Add frame to database")
    @describe(name="Frame name", group="Bit / Gem / Special / Valentines / Springtide / Halloween / Festivus",
              colour="Frame colour", other="Common words inside name (e.g. Bride for bridesmaid",
              img="Transparent image of frame", url="URL link")
    @guilds(guild)
    @check(cog_check_admin)
    @log_as("/frame add")
    async def frame_add(
            self, interaction: Interaction,
            name: str,
            group: str,
            colour: str,
            img: Attachment,
            other: Optional[str],
            url: Optional[str]
    ):

        global all_frames

        # Generate tags
        group = group.replace("bit", "bit basic").replace("gem", "gem carousel") \
            .replace("valentines", "event valentines valentine") \
            .replace("anniversary", "event anniversary birthday") \
            .replace("springtide", "event springtide spring") \
            .replace("halloween", "event halloween") \
            .replace("festivus", "event festivus")
        tags = name.split(" ") + group.split(" ") + colour.split(" ")
        if other is not None:
            tags += other.split()

        # Set URL
        if url is None:
            url = name.replace(" ", "").replace("'", "")

        # Save data to file and frame cog
        frame = dict(name=name, tags=tags, url=url)
        all_frames.append(frame)
        all_frames = sorted(all_frames, key=lambda x: x["name"])

        await awrite_json("frames", all_frames)
        await img.save(Path(f"data/frames/{url}.png"))

        # Send message
        embed = Embed(
            title=f"{title(name)} Frame",
            description=f"**URL:** {url}\n**Tags:** {', '.join(tags)}",
            colour=Colour.light_grey())
        embed.set_image(url=f"https://d2l56h9h5tj8ue.cloudfront.net/images/frames/frame-{url}.jpg")
        await interaction.response.send_message("Successfully added:", embed=embed)

    @command(name="shop", description="Custom frame shop with all frames")
    @rename(options="tags")
    @describe(options="Custom tags to start the frame shop with")
    @cooldown(1, 20.0)
    @log_as("/frame shop")
    async def frame_shop(self, interaction: Interaction, options: Optional[str]):

        frames = all_frames.copy()
        index = 0
        detailed_mode = True

        if options is not None:
            frames = filter_frames(options, frames)[1]

        # For view reset
        def reset_frames():
            nonlocal frames
            frames = all_frames.copy()

        class FrameShopView(View):

            def __init__(self):
                super().__init__(timeout=30)

            @button(emoji="🔼", row=0)
            async def button_s1(self, interaction_: Interaction, _):

                nonlocal index

                index = (index - 1) % len(frames)
                await interaction_.response.edit_message(embed=get_embed())

            @button(emoji="🔽", row=1)
            async def button_a1(self, interaction_: Interaction, _):

                nonlocal index

                index = (index + 1) % len(frames)
                await interaction_.response.edit_message(embed=get_embed())

            @button(emoji="⏫", row=0)
            async def button_s5(self, interaction_: Interaction, _):

                nonlocal index

                index = (index - 5) % len(frames)
                await interaction_.response.edit_message(embed=get_embed())

            @button(emoji="⏬", row=1)
            async def button_a5(self, interaction_: Interaction, _):

                nonlocal index

                index = (index + 5) % len(frames)
                await interaction_.response.edit_message(embed=get_embed())

            @button(emoji="🔄", row=0)
            async def button_reset(self, interaction_: Interaction, _):

                nonlocal index

                reset_frames()
                index = 0
                await interaction_.response.edit_message(embed=get_embed())

            @button(emoji="🔍", row=1)
            async def button_change_mode(self, interaction_: Interaction, _):

                nonlocal detailed_mode

                detailed_mode = not detailed_mode
                await interaction_.response.edit_message(embed=get_embed())

        def get_embed():

            frame = frames[index]

            if detailed_mode:

                if len(frames) == 1:
                    select = ["", "", f"   1. {title(frame['name'])}", "", ""]

                elif len(frames) == 2:
                    select = ["", "", f"   1. {title(frame['name'])}", f"   2. {title(frames[1]['name'])}", ""]
                    if index == 1:
                        select.append(select.pop(0))

                elif len(frames) == 3:
                    select = ["", "", f"   1. {title(frame['name'])}", f"   2. {title(frames[1]['name'])}",
                              f"   3. {title(frames[2]['name'])}"]
                    for i in range(index):
                        select.append(select.pop(0))

                elif len(frames) == 3:
                    select = [f"   4. {title(frames[3]['name'])}", "", f"   1. {title(frame['name'])}",
                              f"   2. {title(frames[1]['name'])}", f"   3. {title(frames[2]['name'])}"]
                    for i in range(index):
                        select.append(select.pop(0))

                else:

                    indexes = [index_ % len(frames) for index_ in range(index - 2, index + 3)]
                    # Assemble frame list
                    select = [f" {indexes[i] + 1: >3}. {title(frames[indexes[i]]['name'])}" for i in range(5)]

                # Finalize block
                select = [(">" if i == 2 else "-") + select[i] for i in range(5)]
                select.insert(2, "")
                select.insert(4, "")

                tags = frame['tags']
                if "bit" in tags:
                    basic_index = tags.index("basic")
                    info = ["# Type:", "- Basic / Bit",
                            "# Cost:", f"- 2500 {tags[basic_index + 1]} bits\n- 2500 {tags[basic_index + 2]} bits"]
                elif "gem" in tags:
                    info = ["# Type:", "- Carousel / Gem", "# Cost:", "- 1000 gems (in rotation)"]
                elif "special" in tags:
                    info = ["# Type:", "- Special", "# Cost:", "- Special Frames Box"]

                else:
                    event_index = tags.index("event")
                    # Does not container an alias (e.g. springtide spring)
                    if "halloween" in tags or "festivus" in tags:
                        info = ["# Type:", f"- Event / {title(tags[event_index + 1])} {tags[event_index + 2]}",
                                "# Cost:", "- During event only"]
                    else:
                        info = ["# Type:", f"- Event / {title(tags[event_index + 1])} {tags[event_index + 3]}",
                                "# Cost:", "- During event only"]

                info = "\n".join(f"{line: <27}" for line in info)
                select = "\n".join(f"{line: <27}" if line not in ("-", "") else line for line in select)

                embed = Embed(
                    title="Frame Shop",
                    description=f"**Information**\n```md\n{info}\n```\n**Selection**\n```c\n{select}\n```",
                    colour=Colour.light_grey())
                embed.set_thumbnail(
                    url=f"https://d2l56h9h5tj8ue.cloudfront.net/images/frames/frame-{frames[index]['url']}.jpg")

            else:

                embed = Embed(
                    title="Frame Shop",
                    description=f"{title(frame['name'])} Frame",
                    colour=Colour.light_grey())
                embed.set_image(
                    url=f"https://d2l56h9h5tj8ue.cloudfront.net/images/frames/frame-{frames[index]['url']}.jpg")

            embed.set_footer(text="Type a tag to filter the frames")

            return embed

        await interaction.response.send_message(interaction.user.mention, embed=get_embed(), view=FrameShopView())

        def message_check(message_: Message):

            # Incorrect server
            if message_.author.id != interaction.user.id and message_.channel.id != interaction.channel_id:
                return False
            if message_.author.id == self.bot.user.id and message_.channel.id == interaction.channel_id and \
                    message_.content[2:20] == str(interaction.user.id):
                return False

            nonlocal frames, index
            valid_tag, possible_frames = filter_frames(message_.content, all_frames.copy())

            if valid_tag:
                frames = possible_frames
                index = 0

            return valid_tag

        while True:

            try:
                message = await self.bot.wait_for("message", timeout=60, check=message_check)
                if message.author.id == self.bot.user.id:
                    break

            except TimeoutError:
                break

            else:
                await interaction.edit_original_message(embed=get_embed())

    @command(name="tags", description="List of tags for frame commands")
    @log_as("/frame tags")
    async def frame_tags(self, interaction: Interaction):

        embed = Embed(title="Frame Tags", colour=Colour.light_grey())
        embed.add_field(
            name="Bit tags",
            value="*All bit types*",
            inline=False)
        embed.add_field(
            name="Color tags",
            value="red, orange, yellow, green, blue, purple, pink, brown, black, gray, grey, white",
            inline=False)
        embed.add_field(
            name="Event tags",
            value="anniversary, birthday, festivus, halloween, spring, valentine, valentines",
            inline=False)
        embed.add_field(
            name="Bit tags",
            value="basic, bit, bits, carousel, event, gem, gems, special",
            inline=False)

        await interaction.response.send_message(interaction.user.mention, embed=embed)

    @cooldown(1, 20.0)
    @log_as("Test Frames On")
    async def test_frames_on(self, interaction: Interaction, message: Message):

        ping = interaction.user.mention
        reply = interaction.response.send_message

        if not is_card_embed("Character Lookup", message):
            await reply("Message must be a character lookup", ephemeral=True)
            return

        await interaction.response.send_message(f"{ping}, please enter the tags of the frame(s) you want to test.")

        def message_check(message_: Message):
            return (message_.author.id == interaction.user.id and message_.channel.id == interaction.channel.id) or \
                   (message_.author.id == self.bot.user.id and message_.channel.id == interaction.channel.id and
                    message_.content[2:20] == str(interaction.user.id))

        try:
            tag_message = await self.bot.wait_for("message", timeout=45, check=message_check)
            if tag_message.author.id == self.bot.user.id:
                return
        except TimeoutError:
            return

        success, frames = filter_frames(tag_message.content, all_frames.copy())

        if not success:
            await tag_message.reply("Invalid tags.")

        frames = frames[:10]
        placement = ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 0), (3, 1), (4, 0), (4, 1))[:len(frames)]
        size = ((1, 1), (2, 1), (3, 1), (3, 2), (3, 2), (3, 2), (4, 2), (4, 2), (5, 2), (5, 2))[len(frames) - 1]
        if message.embeds[0].thumbnail.url is not None:
            character = Image.open(BytesIO(get(message.embeds[0].thumbnail.url).content))
        else:
            character = Image.open(BytesIO(get(message.embeds[0].image.url).content))

        character = character.resize((319, 441))
        file_name = f"frame_test_{interaction.user.id}_{round(interaction.created_at.timestamp())}.jpg"
        file_path = f"data/temp/{file_name}"
        result = Image.new("RGB", (size[0] * 381, size[1] * 570), (46, 49, 54))

        for i in range(len(frames)):
            frame = Image.open(f"data/frames/{frames[i]['url']}.png")
            framed_character = Image.new("RGB", (381, 570))
            framed_character.paste(character, (31, 76))
            framed_character.paste(frame, (0, 0), frame)
            result.paste(framed_character, (placement[i][0] * 381, placement[i][1] * 570))

        result.save(file_path)

        embed = Embed(
            title="Frame Test",
            description="**Tested frame(s):** " + ", ".join(f"{title(frame['name'])} frame" for frame in frames),
            colour=Colour.light_grey())
        embed.set_image(url=f"attachment://{file_name}")
        await tag_message.reply(embed=embed, file=File(file_path))

        remove(file_path)
