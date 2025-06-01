import datetime

import discord
from discord.ext import commands

from modules.character import CharacterInfo
from modules.character.dndbeyond import DDBImporter
from modules.character.pathbuilder import PBImporter


# noinspection PyUnusedLocal
async def update_err(context: commands.Context, cid: int):
    await context.send("Unsupported update method! Automatic updates are only available for D&D Beyond and PathBuilder characters.")

# noinspection PyUnusedLocal
async def import_err(context: commands.Context, link: str):
    await context.send("Unsupported import method! Please use a valid D&D Beyond or PathBuilder link.")


class CharacterImporter(commands.Cog):

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
    await bot.add_cog(CharacterImporter(bot))
