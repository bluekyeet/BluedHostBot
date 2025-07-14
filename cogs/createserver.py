import os
import random
import time
import databasehandler
import discord
import requests
import datetime
import re
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

SERVERNAME_REGEX = r'^[a-zA-Z0-9 _-]{3,32}$'

def get_random_port(location_id):
    url = f"https://panel.bluedhost.org/api/application/nodes/{location_id}/allocations"
    headers = {
        "Authorization": f"Bearer {os.getenv('PANELKEY')}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    available_allocations = []
    current_page = 1

    while True:
        response = requests.get(f"{url}?page={current_page}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            allocations = data["data"]
            available_allocations.extend(
                [alloc["attributes"]["id"] for alloc in allocations if not alloc["attributes"]["assigned"]]
            )
            pagination = data["meta"]["pagination"]
            if pagination["current_page"] >= pagination["total_pages"]:
                break
            current_page += 1
        else:
            return "No available ports in the specified location."

    if available_allocations:
        return random.choice(available_allocations)
    else:
        return "No available ports in the specified location."

class createserver(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="createserver", description="Create a server on BluedHost.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.choices(location=[app_commands.Choice(name="Hydrogen | India", value=1),
                                    app_commands.Choice(name="Hydrogen | Singapore ", value=5),
                                    app_commands.Choice(name="Gold | India", value=2),
                                    app_commands.Choice(name="Platinum | France", value=3)])
    @app_commands.describe(servername="The name of the server you want to create.", location="The location of the server.")
    async def createserver(self, interaction: discord.Interaction, servername: str, location: app_commands.Choice[int]):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You don't have an account."), ephemeral=True)
                    return
                goldservers = [2]
                if interaction.user.get_role(1368022648168120430) is None and location.value in goldservers:
                    await interaction.response.send_message(embed=embeds.embed_info("You do not currently own BluedHost Gold."), ephemeral=True)
                    return
                if not re.match(SERVERNAME_REGEX, servername):
                    await interaction.response.send_message(embed=embeds.embed_error("Invalid server name. Server names must be 3-32 characters long and can only contain letters, numbers, dashes, and underscores."), ephemeral=True)
                    return
                if not databasehandler.check_if_user_has_slots(interaction.user.id):
                    await interaction.response.send_message(embed=embeds.embed_info("You have used up all your server slots."), ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embeds.embed_server_creation("Creating server..."))
                    if location.value == 3:
                        port = get_random_port(random.choices([3, 4])[0])
                    else:
                        port = get_random_port(location.value)
                    if port == "No available ports in the specified location.":
                        await interaction.edit_original_response(embed=embeds.embed_server_creation("No available ports in the specified location."))
                        return
                    url = 'https://panel.bluedhost.org/api/application/servers'
                    headers = {
                        "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    payload = {
                      "name": servername,
                      "user": databasehandler.get_user_uid(interaction.user.id),
                      "egg": 1,
                      "docker_image": "ghcr.io/parkervcp/yolks:java_21",
                      "startup": "java -Xms128M -XX:MaxRAMPercentage=95.0 -Dterminal.jline=false -Dterminal.ansi=true -jar {{SERVER_JARFILE}}",
                      "environment": {
                        "BUILD_NUMBER": "latest",
                        "SERVER_JARFILE": "server.jar"
                      },
                      "limits": {
                        "memory": 2048,
                        "swap": 0,
                        "disk": 5120,
                        "io": 500,
                        "cpu": 100
                      },
                      "feature_limits": {
                        "databases": 0,
                        "backups": 0
                      },
                      "allocation": {
                        "default": port
                      }
                    }


                    response = requests.request('POST', url, json=payload, headers=headers)
                    databasehandler.add_server(int(response.json()['attributes']['id']), databasehandler.get_user_uid(interaction.user.id))
                    if response.status_code == 201:
                        try:
                            await interaction.user.send(embed=embeds.embed_server_creation("Successfully created server.\n"
                                                        f"Server Name: {servername}\nLocation: {location.name}\n"
                                                        f"**Resources:**\n"
                                                        f"- Memory: 2GB\n"
                                                        f"- Disk: 5GB\n"
                                                        f"- CPU: 100%\n"
                                                        f"- Link: https://panel.bluedhost.org/server/{response.json()['attributes']['id']}\n"
                                                        f"- Expires in <t:{int((datetime.datetime.now(datetime.UTC).timestamp()//1)+604800)}:R>.\n"
                                                                             f"- /renewserver in <#1367424445886631988> to renew your server."))
                            await interaction.edit_original_response(embed=embeds.embed_server_creation("Server created! Check your DMs for details."))
                        except Exception as e:
                            print(e)
                            await interaction.edit_original_response(embed=embeds.embed_error("Unable to DM you, please open your DMs."))
                            time.sleep(5)
                            await interaction.edit_original_response(embed=embeds.embed_server_creation("Successfully created server.\n"
                                                                             f"Server Name: {servername}\nLocation: {location.name}\n"
                                                                             f"**Resources:**\n"
                                                                             f"- Memory: 2GB\n"
                                                                             f"- Disk: 5GB\n"
                                                                             f"- CPU: 100%\n"
                                                                             f"- Link: https://panel.bluedhost.org/server/{response.json()['attributes']['id']}\n"
                                                                             f"- Expires in <t.{int((datetime.datetime.now(datetime.UTC).timestamp()//1)+604800)}.R>.\n"
                                                                             f"- /renewserver in <#1367424445886631988> to renew your server."))
                    else:
                        await interaction.user.send(embed=embeds.embed_error(message="Something went wrong. Please contact support."))
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Unable to DM you, please open your DMs."), ephemeral=True)


    @createserver.error
    async def createserver_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(createserver(bot), guilds=[discord.Object(id=1367424444850634863)])
