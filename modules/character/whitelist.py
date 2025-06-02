import asyncio

import discord
from discord.ext import commands


class Cooldown:
    def __init__(self, cid, channel, cooldown):
        self.cid = cid
        self.channel = channel
        self.cooldown = cooldown

    async def run(self):
        counter = self.cooldown
        for i in range(counter):
            await asyncio.sleep(1)
            self.cooldown -= 1


class Whitelist(commands.Cog):
    instance: 'Whitelist' = None
    whitelist_help = """
## Whitelist Commands
------------------

**Whitelists:**
    `{prefix}whitelist_channel` <channel> <cooldown> - Whitelist a channel. Cooldown is optional and defaults to 0.
    `{prefix}whitelist_category` <category> <cooldown> - Whitelist a category.
    
**Blacklists:**
    Whitelist will override blacklist.
    `{prefix}blacklist_channel` <channel> - Blacklist a channel.
    `{prefix}blacklist_category` <category> - Blacklist a category.
"""
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.connection = bot.connection
        self.cooldowns: dict[int, list] = {}
        Whitelist.instance = self

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=["allow_channel"])
    async def whitelist_channel(self, context: commands.Context, channel: discord.TextChannel, cooldown: int = 0):
        info = self.bot.db.execute("SELECT * FROM channels WHERE id = ?", (channel.id,)).fetchone()
        if info is None:
            self.bot.db.execute("INSERT INTO channels (id, whitelisted, cooldown, type) VALUES (?, ?, ?, ?)",
                                (channel.id, 1, cooldown, "text"))
        elif info["whitelisted"] == 1:
            await context.send("Channel already whitelisted!")
            return
        elif info["whitelisted"] == 0:
            self.bot.db.execute("UPDATE channels SET whitelisted = ?, cooldown = ? WHERE id = ?", (1, cooldown, channel.id))
        self.bot.connection.commit()
        await context.send("Channel whitelisted!")

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=["deny_channel"])
    async def blacklist_channel(self, context: commands.Context, channel: discord.TextChannel):
        info = self.bot.db.execute("SELECT * FROM channels WHERE id = ?", (channel.id,)).fetchone()
        if info is None:
            self.bot.db.execute("INSERT INTO channels (id, whitelisted, cooldown, type) VALUES (?, ?, ?, ?)",
                                (channel.id, 0, 0, "text"))
        if info["whitelisted"] == 0:
            await context.send("Channel already blacklisted!")
            return
        else:
            self.bot.db.execute("UPDATE channels SET whitelisted = ?, cooldown = ? WHERE id = ?", (0, 0, channel.id))
        self.bot.connection.commit()
        await context.send("Channel blacklisted!")

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=["allow_category"])
    async def whitelist_category(self, context: commands.Context, category: discord.CategoryChannel):
        info = self.bot.db.execute("SELECT * FROM channels WHERE id = ?", (category.id,)).fetchone()
        if info is None:
            self.bot.db.execute("INSERT INTO channels (id, whitelisted, cooldown, type) VALUES (?, ?, ?, ?)",
                                (category.id, 1, 0, "category"))
        if info["whitelisted"] == 1:
            await context.send("Category already whitelisted!")
            return
        else:
            self.bot.db.execute("UPDATE channels SET whitelisted = ?, cooldown = ? WHERE id = ?", (1, 0, category.id))
        self.bot.connection.commit()
        await context.send("Category whitelisted!")

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=["deny_category"])
    async def blacklist_category(self, context: commands.Context, category: discord.CategoryChannel):
        info = self.bot.db.execute("SELECT * FROM channels WHERE id = ?", (category.id,)).fetchone()
        if info is None:
            self.bot.db.execute("INSERT INTO channels (id, whitelisted, cooldown, type) VALUES (?, ?, ?, ?)",
                                (category.id, 0, 0, "category"))
        if info["whitelisted"] == 0:
            await context.send("Category already blacklisted!")
            return
        else:
            self.bot.db.execute("UPDATE channels SET whitelisted = ?, cooldown = ? WHERE id = ?", (0, 0, category.id))
        self.bot.connection.commit()
        await context.send("Category blacklisted!")

    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def enable_whitelist(self, context: commands.Context):
        self.bot.db.execute("UPDATE config SET whitelist_enabled = 1 WHERE server_id = ?", (context.guild.id,))
        self.bot.connection.commit()
        await context.send("Whitelist enabled!")

    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def disable_whitelist(self, context: commands.Context):
        self.bot.db.execute("UPDATE config SET whitelist_enabled = 0 WHERE server_id = ?", (context.guild.id,))
        self.bot.connection.commit()
        await context.send("Whitelist disabled!")

    async def set_cooldown(self, cooldown, channel, cid):
        if cooldown > 0:
            if cid not in self.cooldowns:
                self.cooldowns[cid] = []

            cooldown_obj = Cooldown(cid, channel, cooldown)
            self.cooldowns[cid].append(cooldown_obj)
            task = asyncio.create_task(self.cooldowns[cid][-1].run())
            task.set_name(f"Cooldown for {cid} in {channel.id}")
            task.add_done_callback(lambda _: self.cooldowns[cid].remove(cooldown_obj))

    def get_character_cooldown(self, cid: int, channel: discord.TextChannel):
        if cid in self.cooldowns:
            for i in self.cooldowns[cid]:
                if i.channel == channel:
                    if i.cooldown <= 0:
                        self.cooldowns[cid].remove(i)
                        return False
                    else:
                        return True

    def get_channel_cooldown(self, channel_id, category_id):
        channel_info = self.bot.db.execute(
            "SELECT * FROM channels WHERE id = ? AND whitelisted = 1", (channel_id,)).fetchone()
        category_info = None
        if not channel_info and category_id:
            category_info = self.bot.db.execute(
                "SELECT * FROM channels WHERE id = ? AND whitelisted = 1", (category_id,)).fetchone()
            if not category_info:
                return
        if not channel_info and not category_info:
            return

        cooldown = channel_info["cooldown"] if channel_info is not None else category_info["cooldown"]
        return cooldown


async def setup(bot):
    await bot.add_cog(Whitelist(bot))