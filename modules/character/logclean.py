from typing import Callable, Coroutine, Any

import discord
from discord.ext import commands

from modules.character import LogCleaners

Cleaner = Callable[[commands.Bot, discord.Message], Coroutine[Any, Any, tuple[int, int]]]

class LogCleanup(commands.Cog):
    cache: dict[int, int] = {}
    cleanup: dict[str, Cleaner] = {"Catalogger": LogCleaners.catalogger, "Dyno": LogCleaners.dyno}

    def __init__(self, bot):
        self.bot = bot
        enabled_list = self.bot.db.execute("SELECT server_id, log_clean_enabled FROM config").fetchall()
        self.enabled: dict[int, int] = {i["server_id"]: i["log_clean_enabled"] for i in enabled_list}

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def enable_log_cleanup(self, context: commands.Context):
        self.bot.db.execute("UPDATE config SET log_clean_enabled = 1 WHERE server_id = ?", (context.guild.id,))
        self.enabled[context.guild.id] = 1
        self.bot.connection.commit()
        await context.send("Log cleanup enabled!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def disable_log_cleanup(self, context: commands.Context):
        self.bot.db.execute("UPDATE config SET log_clean_enabled = 0 WHERE server_id = ?", (context.guild.id,))
        self.enabled[context.guild.id] = 0
        self.bot.connection.commit()
        await context.send("Log cleanup disabled!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return
        if message.guild.id not in self.enabled:
            self.enabled[message.guild.id] = 0
        if not self.enabled[message.guild.id] or not message.author.bot:
            return
        username = message.author.display_name
        if "#" in username:
            username = username[:username.index("#")]
        if username in self.cleanup:
            ret = await self.cleanup[username](self.bot, message)
            print("Returned:", ret)
            if ret is None:
                return
            message_id, user_id = ret
            if message_id == 0 or user_id == 0:
                return
            print("Cache:", self.cache)
            print("Deleting message", message_id, "from user", user_id)
            if message_id in self.cache:
                print("Message found in cache")
                if user_id == self.cache[message_id]:
                    await message.delete()
                    del self.cache[message_id]

async def setup(bot):
    await bot.add_cog(LogCleanup(bot))