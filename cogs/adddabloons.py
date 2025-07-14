import discord
import databasehandler
import embeds
from discord import app_commands
from discord.ext import commands

class adddabloons(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="adddabloons", description="Give an amount of dabloons to another user.")
    async def adddabloons(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if interaction.user.get_role(1367710634095022192) is None:
            await interaction.response.send_message(embed=embeds.embed_warning(message="You don't have permission to use this command."), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(user.id) or databasehandler == 400:

                    await interaction.response.send_message(embed=embeds.embed_warning(message="The user you are trying to add dabloons to doesn't have an account."), ephemeral=True)
                    return
                databasehandler.update_coin_count(user.id, amount)

                await interaction.response.send_message(embed=embeds.embed_success(message=f"Added {amount} dabloons to <@{user.id}> successfully. They have {databasehandler.check_coin_count(user.id)} dabloons now."))
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(adddabloons(bot), guilds=[discord.Object(id=1367424444850634863)])
