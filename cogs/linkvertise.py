import datetime
import os
import discord
import databasehandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

class linkvertise(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="linkvertise", description="Go to the Linkvertise link generation page to earn coins.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def upgrade(self, interaction: discord.Interaction):
        if interaction.channel.id != 1367424595824607302:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have an account."), ephemeral=True)
                    return
                linkvertise_data = databasehandler.get_linkvertise_info(interaction.user.id)

                if linkvertise_data == 400:
                    await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)
                    return
                linkvertise_count = int(linkvertise_data[0])
                linkvertise_date = linkvertise_data[1]

                if linkvertise_count >= int(os.getenv("LINKVERTISE")):
                    if datetime.date.fromisoformat(linkvertise_date) < datetime.date.today():
                        databasehandler.update_linkvertise_count(interaction.user.id, 0)
                    else:
                        await interaction.response.send_message(embed=embeds.embed_warning("You have reached the maximum amount of Linkvertise attempts today."), ephemeral=True)
                        return

                await interaction.response.send_message(
                    embed=embeds.embed_info(f'Your Linkvertise link generation page is [here](https://linkvertise.bluedhost.org/generate?user_id={interaction.user.id}).'), ephemeral=True
                )

            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)

    @upgrade.error
    async def upgrade_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(linkvertise(bot), guilds=[discord.Object(id=1367424444850634863)])
