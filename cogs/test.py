import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands


class test(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="test", description="The current time where the bot is hosted!")
    async def test(self, interaction: discord.Interaction):
        if interaction.user.id != 548949604113186847:
            await interaction.response.send_message("Admin only", ephemeral=True)
        else:
            try:
                await self.bot.tree.sync(guild=discord.Object(id=1367424444850634863))
                await interaction.user.send("The current time where the bot is hosted is " + datetime.now().strftime("%H:%M:%S"))
                await interaction.response.send_message('The current time where the bot is hosted is ' + datetime.now().strftime("%H:%M:%S"))
            except Exception as e:
                print(e)
                await interaction.response.send_message("Unable to DM you, please open your DMs.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(test(bot), guilds=[discord.Object(id=1367424444850634863)])
