import discord
import databasehandler
from discord import app_commands
from discord.ext import commands

class dabloons(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="dabloons", description="Check how many dabloons you have.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def dabloons(self, interaction: discord.Interaction):
        if interaction.channel.id != 1367424595824607302:
            await interaction.response.send_message("Wrong channel!", ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message("You don't have an account.", ephemeral=True)
                    return
                await interaction.response.send_message(f"You have {int(databasehandler.check_coin_count(interaction.user.id))} dabloons!")
            except Exception as e:
                print(e)
                await interaction.response.send_message("Something went wrong. Please contact support.", ephemeral=True)
    @dabloons.error
    async def dabloons_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(dabloons(bot), guilds=[discord.Object(id=1367424444850634863)])
