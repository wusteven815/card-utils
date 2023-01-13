from discord import ButtonStyle
from discord import Interaction
from discord.ui import View
from discord.ui import button


class ConfirmView(View):

    def __init__(self):
        super().__init__(timeout=30)
        self.confirmed = None

    @button(label="Yes", style=ButtonStyle.green)
    async def yes(self, interaction_, __):
        self.confirmed = True
        await interaction_.response.defer()
        self.stop()

    @button(label="No", style=ButtonStyle.red)
    async def no(self, interaction_: Interaction, __):
        self.confirmed = False
        await interaction_.response.defer()
        self.stop()