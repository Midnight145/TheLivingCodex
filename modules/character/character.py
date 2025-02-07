import datetime

import aiohttp
import discord
from discord.ext import commands
from math import ceil

from modules.character.CharacterInfo import CharacterInfo
from modules.character.util import Util
from modules.character.whitelist import Whitelist


# noinspection DuplicatedCode
class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute(
            'CREATE TABLE IF NOT EXISTS "characters" ( "id" INTEGER PRIMARY KEY, "name" TEXT, "race" TEXT, '
            '"classes" TEXT, "image" TEXT, "backstory" TEXT, "link" TEXT, "owner" INTEGER)')
        self.bot.db.execute("CREATE TABLE IF NOT EXISTS prefixes (id INTEGER PRIMARY KEY, cid INTEGER, prefix TEXT)")
        self.bot.db.execute("CREATE TABLE IF NOT EXISTS proxies (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cid INTEGER, channel INTEGER, thread INTEGER)")
        self.bot.db.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER, whitelisted BOOLEAN, cooldown INTEGER, type TEXT)")
        self.bot.connection.commit()
        self.api = "https://character-service.dndbeyond.com/character/v5/character/"


    @commands.command(aliases=['import'])
    async def import_character(self, context: commands.Context, ddb_link: str):
        char_id = ddb_link.split("/")[-1]
        link = self.api + char_id
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status == 403:
                    return await context.send(
                        f"Failed to fetch character data! Make sure your character is set to public [here](https://www.dndbeyond.com/characters/{char_id}/builder/home/basic)")
                if resp.status != 200:
                    return await context.send("Failed to fetch character data!")
                data = (await resp.json())["data"]
        character = CharacterInfo(data)

        self.bot.db.execute("INSERT INTO characters (name, owner, backstory, race, classes, image, link) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (character.name, context.author.id, character.backstory, character.race, character.classes, character.image, ddb_link))
        self.bot.connection.commit()
        cid = self.bot.db.lastrowid
        embed = discord.Embed(
            title=f"Character Created",
            description=f"Name: {character.name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_image(url=character.image)
        await context.send(embed=embed)
        await context.send(f"Character created with character id {cid}, run `>add_prefix <id>` to add a prefix to "
                           f"this character!")

    @commands.command(aliases=["update"])
    async def update_character(self, context: commands.Context, cid: int):
        if not await self.check_character(context, cid):
            return
        ddb_link = self.bot.db.execute("SELECT link FROM characters WHERE id = ?", (cid,)).fetchone()[0]
        link = ddb_link.split("/")[-1]
        link = self.api + link
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status != 200:
                    return await context.send("Failed to fetch character data!")
                data = (await resp.json())["data"]
        character = CharacterInfo(data)
        self.bot.db.execute(
            "UPDATE characters SET (name, owner, backstory, race, classes, image, link) = (?, ?, ?, ?, ?, ?, ?) WHERE id = ?",
            (character.name, context.author.id, character.backstory, character.race, character.classes, character.image, ddb_link), cid)
        self.bot.connection.commit()
        await context.send(f"Character {character.name} successfully updated!")

    @commands.command(aliases=["delete"])
    async def delete_character(self, context: commands.Context, cid: int):
        if not await self.check_character(context, cid):
            return
        self.bot.db.execute("DELETE FROM characters WHERE id = ?", (cid,))
        self.bot.db.execute("DELETE FROM prefixes WHERE cid = ?", (cid,))
        self.bot.db.execute("DELETE FROM proxies WHERE cid = ?", (cid,))
        self.bot.connection.commit()
        await context.send("Character deleted!")

    @commands.command(aliases=['view'])
    async def view_character(self, context: commands.Context, cid: int):
        if not await self.check_character(context, cid, check_owner=False):
            return
        character = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        embed = Util.generate_character_embed(character)

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
            await context.send(Util.help_str + "" + Whitelist.whitelist_help)
        else:
            await context.send(Util.help_str)

    async def check_character(self, context, cid, check_owner=True):
        character = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        if character is None:
            await context.send("Character not found!")
            return False
        if check_owner and character["owner"] != context.author.id:
            await context.send("You do not own this character!")
            return False
        return True

async def setup(bot):
    await bot.add_cog(Character(bot))
