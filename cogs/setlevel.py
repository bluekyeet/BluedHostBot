import os
import discord
import requests
import databasehandler
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands

import embeds

load_dotenv()

levels = (100,2048,5120),(175,3584,7680),(200,4608,8192),(225,5632,10240),(250,6656,12288),(300,8192,15360)

class setlevel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="setlevel", description="Set the level of a server.")
    @app_commands.describe(server_id="The ID of the server you want to set the level for.", level="The level you want to set the server to.")
    async def adddabloons(self, interaction: discord.Interaction, server_id: int, level: int):
        if interaction.user.get_role(1367710634095022192) is None:
            await interaction.response.send_message(embed=embeds.embed_warning("You don't have permission to use this command."), ephemeral=True)
        else:
            try:
                if not databasehandler.check_if_server_exists(server_id) or databasehandler == 400:
                    await interaction.response.send_message(
                        embed=embeds.embed_warning("The server you are trying upgrade doesn't exist."), ephemeral=True)
                    return
                databasehandler.upgrade_server(server_id, level)
                if level < 0 or level > len(levels):
                    await interaction.response.send_message(embed=embeds.embed_error("Invalid level. Level must be between 0 and 5."), ephemeral=True)
                    return

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
                cpu, memory, disk = levels[level]
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
                await interaction.response.send_message(embed=embeds.embed_success(f"Successfully set server with ID of {server_id} to level {level}."))
                requests.patch(url=url, json=payload, headers=headers)
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(setlevel(bot), guilds=[discord.Object(id=1367424444850634863)])
