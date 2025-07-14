import discord
import databasehandler
import os
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, user_id: int, server_id: int):
        super().__init__()
        self.user_id = user_id
        self.server_id = server_id

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger, emoji="❗", custom_id="alert_button")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.send_message(embed=embeds.embed_success("Server deleted successfully!"))
        response = requests.delete(
            f"https://panel.bluedhost.org/api/application/servers/{self.server_id}",
            headers={
                "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()
        server_info = databasehandler.get_single_server_info(self.server_id)
        server_level = server_info[0]
        databasehandler.delete_server(self.server_id, self.user_id)
        if server_level == 0:
            return
        elif server_level >= 1:
            databasehandler.update_coin_count(interaction.user.id, server_level * 1000)

class deleteserver(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="deleteserver", description="See your server information.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to delete.")
    async def deleteserver(self, interaction: discord.Interaction, server_id: int):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You don't have an account."), ephemeral=True)
                    return
                if not databasehandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You do not own this server."), ephemeral=True)
                    return
                view = ConfirmDeleteView(interaction.user.id, server_id)
                await interaction.response.send_message(embed=embeds.embed_info("Are you sure you want to delete your server? This action cannot be undone. All purchased upgrades will be refunded. Click 'Yes' to confirm."), view=view)
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)

    @deleteserver.error
    async def deleteserver_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(deleteserver(bot), guilds=[discord.Object(id=1367424444850634863)])
