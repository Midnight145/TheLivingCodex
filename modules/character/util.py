import datetime
import json

import discord
from discord.ext import commands


class Util(commands.Cog):
    help_str = """
## Command Reference
-----------------

**Character Management:**
    `>import <url>` - Imports a given character from a D&D Beyond link. The character sheet has to be public. (Edit --> Home --> Character Privacy --> Public)
    `>update <id>` - Fetches the latest information for a character from D&D Beyond 
    `>delete <id>` - Delete a character. You must be the owner of the character to delete it.
    
    `>add_prefix <id> <prefix>` - Add a prefix to a character. This prefix will be used to trigger the character. For example, if you add the prefix "!" to a character, you can trigger it by sending "!<message>" in any channel the bot can see.
    `>remove_prefix <id> <prefix>` - Remove a prefix from a character. You must be the owner of the character to remove a prefix.

    `>list` - List all of your characters. This will also show character ids, used in other commands.    
    `>view <id>` - View a character's information. This will show all information about the character, including the owner
    
    `>proxy <prefix|id>` - Proxy as a character in the current channel. This will allow you to send messages as the character without needing to use a prefix. Starting a message with '[' will disable proxying for that message.
    `>unproxy` - Disable proxying in the current channel.
    
**Reactions:**
    ✖ - Delete a proxied message. You must be the owner of the character to delete it.
    📝 - Edit a proxied message. You must be the owner of the character to edit it. 
    📋 - View the character's information.
    ❔ - View this help message.
"""

    base_link = "https://www.dndbeyond.com/"
    instance: 'Util' = None
    def __init__(self, bot):
        self.bot = bot
        Util.instance = self

    async def create_webhook(self, channel):
        webhooks = await channel.webhooks()
        for i in webhooks:
            if i.user.id == self.bot.user.id:
                webhook = i
                break
        else:
            webhook = await channel.create_webhook(name="hook")

        return webhook

    def fetch_char_info(self, content, author):
        prefixes = self.bot.db.execute("SELECT * FROM prefixes").fetchall()
        found_prefix = None
        found_prefixes = [i for i in prefixes if content.startswith(i["prefix"])]
        char = None
        for prefix in found_prefixes:
            potential_cid = prefix["cid"]
            tmp = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (potential_cid,)).fetchone()
            if tmp["owner"] != author:
                continue
            else:
                found_prefix = prefix
                char = tmp
        return char, found_prefix

    @staticmethod
    def fetch_channel_info(context):

        channel = context.channel.id
        thread = 0
        if isinstance(context.channel, discord.Thread):
            channel = context.channel.parent.id
            thread = context.channel.id
        return channel, thread

    @staticmethod
    def generate_character_embed(character):
        embed = discord.Embed(
            title=f"Info for {character['name']}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{character['owner']}>")
        embed.add_field(name="Link", value=f"[{character['name']}]({character['link']})")
        embed.add_field(name="Race", value=character["race"], inline=False)

        class_str = ""
        classes = json.loads(character["classes"])
        base_str = "{} - [{}]({})"
        base_sub_str = "{} - [{}]({}) | [{}]({})"
        for i in classes:
            if i["subclass"] == "":
                class_str += base_str.format(i["level"], i["name"], Util.base_link + i["url"]) + "\n"
            else:
                class_str += base_sub_str.format(i["level"], i["name"], Util.base_link + i["url"], i["subclass"], Util.base_link + i["subclass_url"]) + "\n"

        embed.add_field(name="Class(es)", value=class_str, inline=False)

        if len(character["backstory"]) > 1024:
            embed.add_field(name="Backstory", value=character["backstory"][:1021] + "...", inline=False)
        else:
            embed.add_field(name="Backstory", value=character["backstory"], inline=False)
        embed.set_image(url=character["image"])
        return embed


async def setup(bot):
    await bot.add_cog(Util(bot))
