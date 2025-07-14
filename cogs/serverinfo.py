import datetime
import os
import requests
import discord
import databasehandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

class serverinfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="serverinfo", description="See your server information.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to see.")
    async def serverinfo(self, interaction: discord.Interaction, server_id: int = None):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning("Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have an account."), ephemeral=True)
                    return
                if server_id is not None:
                    if not databasehandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                        await interaction.response.send_message(embed=embeds.embed_warning("You don't own that server."), ephemeral=True)
                        return
                    server_info = databasehandler.get_single_server_info(server_id)
                    if server_info == 400:
                        await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)
                        return
                    server_level = server_info[0]
                    server_expire_date = server_info[1]
                    if int(server_expire_date)+604800 == datetime.datetime.now(datetime.UTC).timestamp():
                        server_expire_date = "Expired. Renew with /rewewserver"
                    else:
                        server_expire_date = f"<t:{int(server_expire_date)+604800}:R>"
                    get_server_name_url = f"https://panel.bluedhost.org/api/application/servers/{server[0]}"
                    get_server_info_headers = {
                        "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    get_server_name_response = requests.get(get_server_name_url, headers=get_server_info_headers)
                    get_server_name_response_json = get_server_name_response.json()
                    server_name = get_server_name_response_json['attributes']['name']
                    await interaction.response.send_message(embed=embeds.embed_server_info(f"- Server Name: {server_name}\n"
                                                            f"- Server ID: {server_id}\n"
                                                            f"- Server Link: https://panel.bluedhost.org/server/{server_id}\n"
                                                            f"- Server Level: {server_level}\n"
                                                            f"- Expiry: {server_expire_date}"))
                else:
                    if not databasehandler.check_if_user_has_any_servers(interaction.user.id):
                        await interaction.response.send_message("You don't have any servers.", ephemeral=True)
                        return
                    server_info = databasehandler.get_all_servers_info(interaction.user.id)
                    if server_info == 400:
                        await interaction.response.send_message("Something went wrong. Please contact support.", ephemeral=True)
                        return
                    server_information = ""
                    for server in server_info:
                        get_server_name_url = f"https://panel.bluedhost.org/api/application/servers/{server[0]}"
                        get_server_info_headers = {
                            "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        }
                        get_server_name_response = requests.get(get_server_name_url, headers=get_server_info_headers)
                        get_server_name_response_json = get_server_name_response.json()
                        server_name = get_server_name_response_json['attributes']['name']
                        server_id = server[0]
                        server_level = server[1]
                        server_expire_date = server[2]
                        if int(server_expire_date)+604800 == datetime.datetime.now(datetime.UTC).timestamp():
                            server_expire_date = "Expired. Renew with /renewserver"
                        else:
                            server_expire_date = f"<t:{int(server_expire_date)+604800}:R>"
                        server_information += f"- Server Name: {server_name}\n"
                        server_information += f"- Server ID: {server_id}\n"
                        server_information += f"- Server Level: {server_level}\n"
                        server_information += f"- Expiry: {server_expire_date}\n\n"
                    server_information += f"**Total Servers:** {len(server_info)}"
                    await interaction.response.send_message(embed=embeds.embed_server_info(server_information))
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)

    @serverinfo.error
    async def serverinfo_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(serverinfo(bot), guilds=[discord.Object(id=1367424444850634863)])
