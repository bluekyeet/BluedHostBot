import discord
import databasehandler
from discord import app_commands
from discord.ext import commands

import embeds


class userinfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="userinfo", description="Check the information of your account.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def userinfo(self, interaction: discord.Interaction):
        if interaction.channel.id != 1367445590795092010:
            await interaction.response.send_message(embed=embeds.embed_warning("Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have an account."), ephemeral=True)
                    return
                userinformation = databasehandler.get_user_info(interaction.user.id)
                dabloons = userinformation[2]
                serverslots = userinformation[6]
                usedslots = userinformation[7]
                await interaction.response.send_message(embed=embeds.embed_userinfo(f"Hello {interaction.user.mention}\nDabloons: {dabloons} dabloons\nServer slots: {usedslots}/{serverslots} servers."))
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)
    @userinfo.error
    async def userinfo_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(userinfo(bot), guilds=[discord.Object(id=1367424444850634863)])
