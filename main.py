import discord
import os
import aiohttp
import sqlite3
import threading
import databasehandler
from server_expire_check import expire_check
from webserver import run_webserver
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()


def initdb():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        discord_id INTEGER PRIMARY KEY,
        user_uid INTEGER NOT NULL,
        coins INTEGER DEFAULT 0,
        claimed_boost_reward INTEGER DEFAULT 0,
        lvcount INTEGER DEFAULT 0,
        lvcount_date TEXT DEFAULT NULL,
        avaliable_server_slots INTEGER DEFAULT 1,
        used_server_slots INTEGER DEFAULT 0
    )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            server_id INTEGER PRIMARY KEY,
            user_uid INTEGER,
            server_level INTEGER DEFAULT 0,
            server_last_renew_date INTEGER
        )
        """)
    c.execute("""
            CREATE TABLE IF NOT EXISTS invite (
                inviter INTEGER,
                userid INTEGER
            )
            """)
    conn.commit()
    conn.close()

invite_cache = {}

class bluedhostbot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix='#',
            intents=discord.Intents.all(),
            application_id=1367431253141225572
        )
        self.session = None
        self.initial_extensions = ["cogs.claimboost", "cogs.adddabloons", "cogs.setlevel", "cogs.createaccount",
                                   "cogs.createserver", "cogs.userinfo", "cogs.renewserver", "cogs.serverinfo",
                                   "cogs.deleteserver", "cogs.upgrade", "cogs.givedabloons", "cogs.linkvertise",
                                   "cogs.buy", "cogs.help"]

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await self.tree.sync(guild=discord.Object(id=1367424444850634863))

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

    async def on_ready(self):
        initdb()
        guild = bot.guilds[0]
        invites = await guild.invites()
        invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_member_join(self, member):
        guild = member.guild
        new_invites = await guild.invites()
        old_invites = invite_cache.get(guild.id, {})
        used_invite = None

        for invite in new_invites:
            if invite.code in old_invites and invite.uses > old_invites[invite.code]:
                used_invite = invite
                break

        invite_cache[guild.id] = {i.code: i.uses for i in new_invites}

        if used_invite:
            now = datetime.now(timezone.utc)
            account_age = now - member.created_at
            inviter = used_invite.inviter

            if not databasehandler.check_if_invite_exists(inviter.id, member.id):
                databasehandler.add_invite(inviter.id, member.id)
                if account_age < timedelta(days=7):
                    await guild.get_channel(1367711528215773274).send(
                        f"Hello {member.mention}, welcome to the server! You were invited by {inviter.name}. Account age is less than 7 days.")
                    return
                await guild.get_channel(1367711528215773274).send(f"Hello {member.mention}, welcome to the server!, you were invited by {inviter.name}. {inviter.mention} has been rewarded with 30 dabloons for inviting you!")
                databasehandler.update_coin_count(inviter.id, 30)
            else:
                await guild.get_channel(1367711528215773274).send(f"Hello {member.mention}, welcome to the server! You were invited by {inviter.name}.")
                return
        else:
            await guild.get_channel(1367711528215773274).send(f"Hello {member.mention}, welcome to the server! No invite detected.")


    async def on_invite_create(self, invite):
        invites = await invite.guild.invites()
        invite_cache[invite.guild.id] = {i.code: i.uses for i in invites}

    async def on_invite_delete(self, invite):
        invites = await invite.guild.invites()
        invite_cache[invite.guild.id] = {i.code: i.uses for i in invites}



webserver_thread = threading.Thread(target=run_webserver)
webserver_thread.daemon = True
webserver_thread.start()
expire_check_thread = threading.Thread(target=expire_check)
expire_check_thread.daemon = True
expire_check_thread.start()
bot = bluedhostbot()
bot.run(os.getenv('TOKEN'))
