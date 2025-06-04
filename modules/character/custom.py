import asyncio
import datetime

import discord
from discord.ext import commands

from modules.character import CharacterInfo


class CustomCharacterModule(commands.Cog):

    __image_api = "https://api.midnight.wtf/images/{}"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['create'])
    async def create_character(self, context: commands.Context):
        await self.create_char_dynamic(context)

        await context.send("Character created!")

    async def create_char_dynamic(self, context: commands.Context):
        try:
            await context.send("Enter character name:")
            name_message = await self.bot.wait_for("message", check=lambda m: m.author == context.author,
                                                   timeout=120)
            await context.send("Enter character race")
            race_message = await self.bot.wait_for("message", check=lambda m: m.author == context.author,
                                                   timeout=120)
            await context.send("Enter character class(es):")
            classes_message = await self.bot.wait_for("message", check=lambda m: m.author == context.author,
                                                      timeout=120)
            await context.send("Enter character image:")
            image_message = await self.bot.wait_for("message", check=lambda m: m.author == context.author,
                                                    timeout=120)

        except asyncio.TimeoutError:
            await context.send("Timed out!")
            return

        name = name_message.content

        if image_message.attachments:
            image = image_message.attachments[0].url
        else:
            image = image_message.content

        self.bot.db.execute(
            "INSERT INTO characters (name, owner, backstory, race, classes, image, link, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, context.author.id, "", race_message.content, classes_message.content,
             "", "", "custom"))
        self.bot.connection.commit()
        embed = discord.Embed(
            title=f"Character Created",
            description=f"Name: {name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_image(url=image)
        cid = self.bot.db.lastrowid
        self.bot.db.execute("UPDATE characters SET image = ? WHERE id = ?", (CustomCharacterModule.__image_api.format(cid), cid))
        self.bot.connection.commit()
        await context.send(embed=embed)
        await context.send(f"Character created with character id {cid}, run `>add_prefix` to add a prefix to "
                           f"this character!")

    @commands.command()
    async def edit_character(self, context: commands.Context, cid: int = None, *, kwargs: str = None):
        possible_keys = ["classes", "race", "name", "backstory"]
        if kwargs is None or cid is None:
            await context.send("Please provide a character ID and the fields to edit in the format `key=value`.\nPossible Keys: `" + ", ".join(possible_keys) + "`")
            return
        arg_words = kwargs.split()
        args = [i.split("=") for i in arg_words]
        args = {arg[0]: arg[1] for arg in args if len(arg) == 2}
        character = CharacterInfo.fetch_character(cid)
        if character.type != "custom":
            await context.send("You can only edit custom characters.")
            return
        for k, v in args:
            if k not in possible_keys:
                await context.send(f"Invalid key: {k}. Possible keys are: {', '.join(possible_keys)}")
                return
            setattr(character, k, v)
        character.write_character(self.bot.db)
        self.bot.connection.commit()

    @commands.command()
    async def edit_image(self, context: commands.Context, cid: int, image: str = None):
        if not await self.check_character(context, cid):
            return

        if image is None and context.message.attachments:
            image = context.message.attachments[0].url
        else:
            if not image:
                await context.send("Please provide an image URL or attach an image.")
                return

        self.bot.db.execute("UPDATE characters SET image = ? WHERE id = ?", (image, cid))
        self.bot.connection.commit()
        await context.send("Image updated successfully!")

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
    await bot.add_cog(CustomCharacterModule(bot))