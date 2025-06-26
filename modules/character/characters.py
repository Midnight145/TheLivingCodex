from math import ceil

import discord
from discord.ext import commands

from modules.character import CharacterInfo
from modules.character.whitelist import Whitelist


class CharacterModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    help_str = """
    ## Command Reference
    -----------------

    **Character Management:**
        `{prefix}import [url]` - Imports a given character from a D&D Beyond, PathBuilder, Scoundry, CompCon, or Demiplane (Daggerheart) link.
              D&D Beyond characters must be public to be imported (Edit --> Home --> Character Privacy --> Public).
              The PathBuilder link is obtained from Menu --> Export --> Export JSON --> View JSON
              Scoundry links are obtained from Export --> Share as URL
              CompCon characters should be exported to a file and attached to the message, instead of adding a link.
                  Pilot Options --> Export Pilot --> Export Data File
        `{prefix}update <id>` - Fetches the latest information for a character
        `{prefix}delete <id>` - Delete a character. You must be the owner of the character to delete it.

        `{prefix}add_prefix <id> <prefix>` - Add a prefix to a character. This prefix will be used to trigger the character. For example, if you add the prefix "!" to a character, you can trigger it by sending "!<message>" in any channel the bot can see.
        `{prefix}remove_prefix <id> <prefix>` - Remove a prefix from a character. You must be the owner of the character to remove a prefix.

        `{prefix}list` - List all of your characters. This will also show character ids, used in other commands.
        `{prefix}view <id>` - View a character's information. This will show all information about the character, including the owner

        `{prefix}proxy <prefix|id>` - Proxy as a character in the current channel. This will allow you to send messages as the character without needing to use a prefix. Starting a message with '[' will disable proxying for that message.
        `{prefix}unproxy` - Disable proxying in the current channel.
"""

    reaction_help_str = """
    **Reactions:**
        ✖ - Delete a proxied message. You must be the owner of the character to delete it.
        📝 - Edit a proxied message. You must be the owner of the character to edit it. 
        📋 - View the character's information.
        ❔ - View this help message.
    """

    custom_help_str = """
    -----------------

    **Custom Characters:**

        `{prefix}create` - Starts interactive character creation
        `{prefix}edit_character <id> <args>` - Edit character attributes
            Usage: `{prefix}edit_character <id> key=value key2=value2 ...`
            Possible keys: `name`, `race`, `classes`, `backstory`
        `{prefix}edit_image <id> [image_url]` - Edit the character's image. You can also attach an image to the message.
            Images for imported characters are editable as well
    """

    config_help_str = """
    -----------------
   
   ** Configuration:**
   
   User Configuration:
   `{prefix}config <option> <value>` - Configure user settings. Options include:
    - `autoreact` - Enable or disable automatic reactions to proxied messages. Set to `true` or `false`.
    
    Server Configuration:
    `{prefix}prefix <new_prefix>` - Change the bot's prefix for the server. This will change the prefix for all commands.
"""

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
        prefix = await self.bot.get_custom_prefix(self.bot, context.message)
        prefix = prefix[-1]
        await context.send(self.help_str.format(prefix=prefix))
        await context.send(self.reaction_help_str.format(prefix=prefix))
        await context.send(self.custom_help_str.format(prefix=prefix))
        if context.guild and context.author.guild_permissions.manage_channels:
            await context.send(Whitelist.whitelist_help.format(prefix=prefix))
        await context.send(self.config_help_str.format(prefix=prefix))

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
    await bot.add_cog(CharacterModule(bot))