import datetime
from math import ceil

import discord
from discord.ext import commands

from modules.character import CharacterInfo
from modules.character.dndbeyond import DDBImporter
from modules.character.pathbuilder import PBImporter
from modules.character.util import Util
from modules.character.whitelist import Whitelist


# noinspection PyUnusedLocal
async def update_err(context: commands.Context, cid: int):
    await context.send("Unsupported update method! Automatic updates are only available for D&D Beyond and PathBuilder characters.")

# noinspection PyUnusedLocal
async def import_err(context: commands.Context, link: str):
    await context.send("Unsupported import method! Please use a valid D&D Beyond or PathBuilder link.")



class CharacterModule(commands.Cog):

    importers = {
        "ddb": DDBImporter.import_character,
        "pb": PBImporter.import_character,
        "_": update_err
    }

    updaters = {
        "ddb": DDBImporter.update_character,
        "pb": PBImporter.update_character,
        "_": update_err
    }

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute(
            'CREATE TABLE IF NOT EXISTS "characters" ( "id" INTEGER PRIMARY KEY, "name" TEXT, "race" TEXT, '
            '"classes" TEXT, "image" TEXT, "backstory" TEXT, "link" TEXT, "owner" INTEGER)')
        self.bot.db.execute("CREATE TABLE IF NOT EXISTS prefixes (id INTEGER PRIMARY KEY, cid INTEGER, prefix TEXT)")
        self.bot.db.execute("CREATE TABLE IF NOT EXISTS proxies (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cid INTEGER, channel INTEGER, thread INTEGER)")
        self.bot.db.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER, whitelisted BOOLEAN, cooldown INTEGER, type TEXT)")
        self.bot.connection.commit()


    @commands.command(aliases=['import'])
    async def import_character(self, context: commands.Context, link: str):
        type_ = self.fetch_import_method(link)
        character = await self.importers.get(type_, self.importers["_"])(context, link)
        if character is None:
            return
        self.bot.db.execute("INSERT INTO characters (name, owner, backstory, race, classes, image, link, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (character.name, context.author.id, character.backstory, character.race, character.classes, character.image, link, type_))
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

        character = CharacterInfo.fetch_character(cid)
        updated = await self.updaters.get(character.type, self.updaters["_"])(context, character.link)
        if updated is None:
            return
        self.bot.db.execute(
            "UPDATE characters SET (name, owner, backstory, race, classes, image, link) = (?, ?, ?, ?, ?, ?, ?) WHERE id = ?",
            (updated.name, context.author.id, updated.backstory, updated.race, updated.classes, updated.image, character.link, cid))
        self.bot.connection.commit()
        await context.send(f"Character {updated.name} successfully updated!")

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

    async def check_character(self, context, cid, check_owner=True):
        character = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        if character is None:
            await context.send("Character not found!")
            return False
        if check_owner and character["owner"] != context.author.id:
            await context.send("You do not own this character!")
            return False
        return True

    @staticmethod
    def fetch_import_method(link: str) -> str:
        if "dndbeyond.com" in link:
            return "ddb"
        if "pathbuilder2e.com" in link:
            return "pb"
        return "_"


async def setup(bot):
    await bot.add_cog(CharacterModule(bot))
