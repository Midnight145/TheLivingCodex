import asyncio

from discord.ext import commands


class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ap'])
    async def add_prefix(self, context: commands.Context, cid: int = None, prefix: str = None):
        if cid is None:
            return await self.add_prefix_dynamic(context)
        if prefix is None:
            return await self.add_prefix_dynamic(context, cid)
        character = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        if character["owner"] != context.author.id:
            await context.send("You do not own this character!")
            return
        self.bot.db.execute("INSERT INTO prefixes (cid, prefix) VALUES (?, ?)", (cid, prefix))
        self.bot.connection.commit()
        await context.send("Prefix added!")

    async def add_prefix_dynamic(self, context, cid: int = None):
        prefix = self.__fetch_prefix(context, cid)
        self.bot.db.execute("INSERT INTO prefixes (cid, prefix) VALUES (?, ?)", (cid, prefix))
        self.bot.connection.commit()
        await context.send("Prefix added!")

    @commands.command(aliases=['rp', 'dp', 'delete_prefix'])
    async def remove_prefix(self, context: commands.Context, cid: int = None, prefix: str = None):
        if cid is None:
            return await self.remove_prefix_dynamic(context)
        if prefix is None:
            return await self.remove_prefix_dynamic(context, cid)
        character = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        if character["owner"] != context.author.id:
            await context.send("You do not own this character!")
            return
        self.bot.db.execute("DELETE FROM prefixes WHERE cid = ? AND prefix = ?", (cid, prefix))
        self.bot.connection.commit()
        await context.send("Prefix removed!")

    async def remove_prefix_dynamic(self, context, cid: int = None):
        prefix = await self.__fetch_prefix(context, cid)
        if prefix is None:
            return
        self.bot.db.execute("DELETE FROM prefixes WHERE cid = ? AND prefix = ?", (cid, prefix))
        self.bot.connection.commit()
        await context.send("Prefix removed!")

    async def __fetch_prefix(self, context: commands.Context, cid: int = None):
        try:
            if cid is None:
                await context.send("Enter character id:")
                cid_message = await self.bot.wait_for("message", check=lambda m: m.author == context.author,
                                                      timeout=120)
                cid = int(cid_message.content)
                character = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
                if character["owner"] != context.author.id:
                    await context.send("You do not own this character!")
                    return None
            await context.send("Enter prefix:")
            prefix_message = await self.bot.wait_for("message", check=lambda m: m.author == context.author, timeout=120)
            return prefix_message.content
        except asyncio.TimeoutError:
            await context.send("Timed out!")
            return None


async def setup(bot):
    await bot.add_cog(Prefix(bot))