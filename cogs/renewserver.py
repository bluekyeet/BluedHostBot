import os
import discord
import requests
import databasehandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

class renewserver(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="renewserver", description="Pay 100 dabloons to renew your server.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to renew.")
    async def renewserver(self, interaction: discord.Interaction, server_id: int):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning("Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have an account."), ephemeral=True)
                    return
                if not databasehandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                    await interaction.response.send_message(embed=embeds.embed_warning("You are not the owner of this server."), ephemeral=True)
                    return
                coincount = databasehandler.check_coin_count(interaction.user.id)
                if coincount < 100:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have enough dabloons to renew your server. You need at least 100 dabloons."))
                    return
                else:
                    databasehandler.update_coin_count(interaction.user.id, -100)
                    databasehandler.renew_server(server_id)
                    await interaction.response.send_message(embed=embeds.embed_success(f"Successfully renewed your server. You have {coincount-100} dabloons left.\nIf your server is suspended, it will be unsuspended within 5-10 minutes."))
                    try:
                        check_suspended_url = f"https://panel.bluedhost.org/api/application/servers/{server_id}"
                        headers = {
                            "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        }
                        response = requests.get(check_suspended_url, headers=headers)
                        response.raise_for_status()
                        json_data = response.json()
                        server_status = json_data["attributes"]["suspended"]
                        if server_status:
                            server_node = json_data["attributes"]["node"]
                            get_node_url = f"https://panel.bluedhost.org/api/application/nodes/{server_node}"
                            node_response = requests.get(get_node_url, headers=headers)
                            node_response.raise_for_status()
                            node_json_data = node_response.json()
                            node_fqdn = node_json_data["attributes"]["fqdn"]
                            freeze_url = f"http://{node_fqdn}:8888/unfreeze/{server_id}"
                            requests.post(freeze_url, headers=headers)
                            renew_url = f"https://panel.bluedhost.org/api/application/servers/{server_id}/unsuspend"
                            requests.post(renew_url, headers=headers)
                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)

    @renewserver.error
    async def renewserver_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(renewserver(bot), guilds=[discord.Object(id=1367424444850634863)])
