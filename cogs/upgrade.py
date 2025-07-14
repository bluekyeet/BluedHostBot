import os
import discord
import databasehandler
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

levels = (175,3584,7680),(200,4608,8192),(225,5632,10240),(250,6656,12288),(300,8192,15360)


class upgrade(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="upgradeserver", description="Upgrade your server.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to upgrade.")
    async def upgrade(self, interaction: discord.Interaction, server_id: int):
        if interaction.channel.id != 1367424595824607302:
            await interaction.response.send_message(embed=embeds.embed_warning("Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have an account."), ephemeral=True)
                    return
                if not databasehandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                    await interaction.response.send_message(embed=embeds.embed_warning("You are not the owner of this server."), ephemeral=True)
                    return
                coin_count = databasehandler.check_coin_count(interaction.user.id)
                current_server_level = int(databasehandler.get_single_server_info(server_id)[0])
                if current_server_level == 5:
                    await interaction.response.send_message(embed=embeds.embed_warning("Your server is already at the maximum level."), ephemeral=True)
                    return
                if coin_count < 1000:
                    await interaction.response.send_message(embed=embeds.embed_warning(f"You don't have enough dabloons to upgrade your server. You need {1000-coin_count} more dabloons."), ephemeral=True)
                    return
                await interaction.response.send_message(embed=embeds.embed_success(f"Upgraded your server to Level {current_server_level+1} successfully! You have {coin_count-1000} dabloons left."))
                databasehandler.update_coin_count(interaction.user.id, -1000)
                databasehandler.upgrade_server(server_id, current_server_level+1)
                getallocationnumberurl = f"https://panel.bluedhost.org/api/application/servers/{server_id}"
                getallocationnumberheaders = {
                    "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
                getallocationnumber = requests.get(url=getallocationnumberurl, headers=getallocationnumberheaders)
                getallocationnumberjson = getallocationnumber.json()
                allocation_id = getallocationnumberjson['attributes']['allocation']
                url = f"https://panel.bluedhost.org/api/application/servers/{server_id}/build"
                headers = {
                    "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
                cpu, memory, disk = levels[current_server_level]
                payload = {
                    "allocation": allocation_id,
                    "memory": memory,
                    "swap": 0,
                    "disk": disk,
                    "io": 500,
                    "cpu": cpu,
                    "feature_limits": {
                        "databases": 0,
                        "backups": 0
                    }
                }
                requests.patch(url=url, json=payload, headers=headers)

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
    await bot.add_cog(upgrade(bot), guilds=[discord.Object(id=1367424444850634863)])
