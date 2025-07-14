import discord
import databasehandler
import embeds
from discord import app_commands
from discord.ext import commands


class claimboostrewards(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="claimboostrewards", description="Claim your boost rewards.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def claimboostrewards(self, interaction: discord.Interaction):
        if interaction.channel.id != 1367424595824607302:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(
                        embed=embeds.embed_warning(message="You don't have an account."), ephemeral=True)
                    return
                if interaction.user.premium_since is None:
                    await interaction.response.send_message(
                        embed=embeds.embed_warning(message="You need to boost the server to claim the reward."), ephemeral=True)
                    return
                if databasehandler.boost_rewards_claimed(interaction.user.id) == 1:
                    await interaction.response.send_message(
                        embed=embeds.embed_warning(message="You have already claimed your boost reward."), ephemeral=True)
                    return
                databasehandler.update_coin_count(interaction.user.id, 1500)
                databasehandler.update_boost_rewards_claimed(interaction.user.id, 1)
                await interaction.response.send_message(
                    embed=embeds.embed_success(message="You have successfully claimed your boost reward of 1500 dabloons."), ephemeral=True)

            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)

    @claimboostrewards.error
    async def claimboostrewardserror(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(claimboostrewards(bot), guilds=[discord.Object(id=1367424444850634863)])
