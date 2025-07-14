import discord
import databasehandler
from discord import app_commands
from discord.ext import commands

import embeds


class givedabloons(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="givedabloons", description="Give an amount of dabloons to another user.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(user="The user you want to give dabloons to", amount="The amount of dabloons you want to give")
    async def givedabloons(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if interaction.channel.id != 1367424595824607302:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_info(message="You don't have an account."), ephemeral=True)
                    return
                if not databasehandler.check_user_exists(user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning(message="The person you are trying to give dabloons to does not have an account."), ephemeral=True)
                    return
                if amount <= 0:
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You cannot give a person negative or zero dabloons."), ephemeral=True)
                    return
                if databasehandler.check_coin_count(interaction.user.id) < amount:
                    await interaction.response.send_message(embed=embeds.embed_warning(message=f"You do not have enough dabloons to give {databasehandler.check_coin_count(interaction.user.id)} dabloons."), ephemeral=True)
                    return
                databasehandler.update_coin_count(interaction.user.id, -amount)
                databasehandler.update_coin_count(user.id, amount)
                await interaction.response.send_message(embed=embeds.embed_success(message=f"You have successfully given {amount} dabloons to <@{user.id}>.\nYou now have {databasehandler.check_coin_count(interaction.user.id)} dabloons left."))
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)

    @givedabloons.error
    async def giveabloonserror(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(givedabloons(bot), guilds=[discord.Object(id=1367424444850634863)])
