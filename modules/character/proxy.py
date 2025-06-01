import asyncio

import discord
from discord.ext import commands

from modules.character import CharacterInfo
from modules.character.dndbeyond.util import Util


# noinspection DuplicatedCode
class Proxy(commands.Cog):
    instance: 'Proxy' = None
    def __init__(self, bot):
        self.bot = bot
        Proxy.instance = self

    @commands.command()
    async def proxy(self, context: commands.Context, prefix: int | str):
        if isinstance(prefix, int):
            char = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (prefix,)).fetchone()
        else:
            char, _ = Util.instance.fetch_char_info(prefix, context.author.id)
        if char is None:
            to_delete = await context.send("Character not found!")
            await asyncio.sleep(3)
            await to_delete.delete()
            return
        channel, thread = Util.fetch_channel_info(context)

        resp = self.bot.db.execute("SELECT * FROM proxies WHERE user_id = ? AND channel = ? AND thread = ?", (context.author.id, channel, thread)).fetchone()
        if resp is not None:
            to_delete = await context.send("You are already proxied in this channel!")
            await asyncio.sleep(3)
            await to_delete.delete()
            return

        self.bot.db.execute("INSERT INTO proxies (user_id, cid, channel, thread) VALUES (?, ?, ?, ?)", (context.author.id, char['id'], channel, thread))
        self.bot.connection.commit()
        to_delete = await context.send("Character proxied!")
        await asyncio.sleep(3)
        await to_delete.delete()

    @commands.command()
    async def unproxy(self, context: commands.Context):
        channel, thread = Util.fetch_channel_info(context)

        self.bot.db.execute("DELETE FROM proxies WHERE user_id = ? AND channel = ? AND thread = ?", (context.author.id, channel, thread))
        self.bot.connection.commit()
        to_delete = await context.send("Character unproxied!")
        await asyncio.sleep(3)
        await to_delete.delete()

    def handle_proxied_message(self, message: discord.Message) -> CharacterInfo | None:
        if isinstance(message.channel, discord.Thread):
            channel = message.channel.parent.id
            thread = True
        else:
            channel = message.channel.id
            thread = False
        resp = self.bot.db.execute("SELECT thread, cid FROM proxies WHERE user_id = ? AND channel = ?", (message.author.id,channel)).fetchall()
        if not resp:
            return None
        if not thread:
            return CharacterInfo.fetch_character(resp[0]["cid"])
        for i in resp:
            if i["thread"] == message.channel.id:
                return CharacterInfo.fetch_character(i["cid"])
        return None


async def setup(bot):
    await bot.add_cog(Proxy(bot))