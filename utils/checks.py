from discord import Interaction
from discord import Message


def cog_check_admin(interaction: Interaction):

    return interaction.user.id == 0


def is_card_embed(embed_title: str, message: Message):

    if message.author.id == 0 and len(message.embeds) != 0:
        return message.embeds[0].title == embed_title

    return False
