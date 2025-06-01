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

    def fetch_char_info(self, content, author) -> tuple[dict, str]:
        prefixes = self.bot.db.execute("SELECT * FROM prefixes WHERE owner = ?", (author,)).fetchall()
        found_prefixes = sorted([i for i in prefixes if content.startswith(i["prefix"])],
                                key = lambda x: len(x["prefix"]), reverse=True)
        found_prefix = found_prefixes[0] if found_prefixes else None
        char = self.bot.db.execute("SELECT * FROM characters WHERE id = ?", (found_prefix["cid"],)).fetchone()

        return char, found_prefix["prefix"]

    @staticmethod
    def fetch_channel_info(context):

        channel = context.channel.id
        thread = 0
        if isinstance(context.channel, discord.Thread):
            channel = context.channel.parent.id
            thread = context.channel.id
        return channel, thread


async def setup(bot):
    await bot.add_cog(Util(bot))
