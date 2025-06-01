from math import ceil

import discord
from discord.ext import commands

from modules.character import CharacterInfo
from modules.character.util import Util
from modules.character.whitelist import Whitelist


class CharacterModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["delete"])
    async def delete_character(self, context: commands.Context, cid: int):
        if not await Util.check_character(context, cid):
            return
        self.bot.db.execute("DELETE FROM characters WHERE id = ?", (cid,))
        self.bot.db.execute("DELETE FROM prefixes WHERE cid = ?", (cid,))
        self.bot.db.execute("DELETE FROM proxies WHERE cid = ?", (cid,))
        self.bot.connection.commit()
        await context.send("Character deleted!")

    @commands.command(aliases=['view'])
    async def view_character(self, context: commands.Context, cid: int):
        if not await Util.check_character(context, cid, check_owner=False):
            return
        character = CharacterInfo.fetch_character(cid)
        embed = character.generate_embed()

        await context.send(embed=embed)

    @commands.command(aliases=['lc', 'list'])
    async def list_characters(self, context: commands.Context):
        chars = self.bot.db.execute("SELECT * FROM characters WHERE owner = ?", (context.author.id,)).fetchall()

        if len(chars) == 0:
            await context.send("You have no characters!")
            return
        embeds = []
        embed_count = ceil(len(chars) / 25)
        for i in range(embed_count):
            embed = discord.Embed(
                title="Your characters",
                color=discord.Color.gold()
            )
            for char in chars[i * 25:(i + 1) * 25]:
                embed.add_field(name=char["name"], value=f"ID: {char['id']}", inline=False)
            embeds.append(embed)
        if len(embeds) > 10:
            await context.send(embeds=embeds[0:10])
            for i in range(len(embeds) // 10):
                await context.send(embeds=embeds[i * 10:(i + 1) * 10])
        else:
            await context.send(embeds=embeds)

    @commands.command()
    async def help(self, context: commands.Context):
        if context.guild and context.author.guild_permissions.manage_channels:
            await context.send(Util.help_str)
            await context.send(Whitelist.whitelist_help)
        else:
            await context.send(Util.help_str)
