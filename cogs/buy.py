import discord
import databasehandler
import embeds
from discord import app_commands
from discord.ext import commands


class buy(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="buy", description="Purchase resources for your server.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.choices(item=[app_commands.Choice(name="Server slot | 500 dabloons", value=1)])
    @app_commands.describe(item="The item you want to buy.")
    async def buy(self, interaction: discord.Interaction, item: app_commands.Choice[int]):
        if interaction.channel.id != 1367424595824607302:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You don't have an account."), ephemeral=True)
                    return
                userinformation = databasehandler.get_user_info(interaction.user.id)
                dabloons = userinformation[2]
                if item.value == 1:
                    if dabloons >= 500:
                        databasehandler.update_coin_count(interaction.user.id, -500)
                        databasehandler.update_server_slots(interaction.user.id, 1)
                        await interaction.response.send_message(embed=embeds.embed_success(message="You have bought a server slot for 500 dabloons.\nYou now have {dabloons - 500} dabloons left."))
                    else:
                        await interaction.response.send_message(embed=embeds.embed_warning(message="You don't have enough dabloons to purchase this item."), ephemeral=True)
                        return
                else:
                    await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)
                    return
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)

    @buy.error
    async def buy_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(buy(bot), guilds=[discord.Object(id=1367424444850634863)])
