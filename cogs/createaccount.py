import random
import string
import discord
import requests
import os
import databasehandler
import re
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

class createaccount(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="createaccount", description="Create an account for BluedHost.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(email="The email of the account you want to create.")
    async def createaccount(self, interaction: discord.Interaction, email: str):
        if interaction.channel.id != 1367445590795092010:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not re.match(EMAIL_REGEX, email):
                    await interaction.response.send_message(
                        embed=embeds.embed_error(message="Email format is invalid."), ephemeral=True)
                    return
                await interaction.response.send_message(embed=embeds.embed_info("Check your DMs."), ephemeral=True)
                await interaction.user.send(embed=embeds.embed_info("Checking system..."))
                if databasehandler.check_user_exists(interaction.user.id):
                    await interaction.user.send(embed=embeds.embed_warning("You already have an account."))
                    return
                else:
                    await interaction.user.send(embed=embeds.embed_info("Creating account..."))
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                    url = 'https://panel.bluedhost.org/api/application/users'
                    headers = {
                        "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    print(interaction.user.id)
                    print(email)
                    payload = {
                        "email": email,
                        "username": str(interaction.user.id),
                        "password": password,
                    }

                    response = requests.request('POST', url, json=payload, headers=headers)
                    print(response.json())
                    print(response.status_code)
                    if response.status_code == 201:
                        await interaction.user.send(embed=embeds.embed_success(f"Successfully created account.\nUsername: {str(interaction.user.id)}\nPassword: {password}\nLink: https://panel.bluedhost.org/"))
                        databasehandler.create_user(interaction.user.id, response.json()['attributes']['id'])
                    elif response.status_code == 422:
                        await interaction.user.send(embed=embeds.embed_warning("You already have an account."))
                    else:
                        await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Unable to DM you, please open your DMs."), ephemeral=True)


    @createaccount.error
    async def createaccount_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(createaccount(bot), guilds=[discord.Object(id=1367424444850634863)])
