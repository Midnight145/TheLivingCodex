import discord
from discord.ext import commands

from modules.character import CharacterInfo


class Util(commands.Cog):



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

    def fetch_char_info(self, content, author) -> tuple[CharacterInfo, str]:
        prefixes = self.bot.db.execute("SELECT * FROM prefixes WHERE owner = ?", (author,)).fetchall()
        found_prefixes = sorted([i for i in prefixes if content.startswith(i["prefix"])],
                                key = lambda x: len(x["prefix"]), reverse=True)
        found_prefix = found_prefixes[0] if found_prefixes else None
        char = CharacterInfo.fetch_character(found_prefix["cid"]) if found_prefix else None

        return char, None if not found_prefix else found_prefix["prefix"]

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
