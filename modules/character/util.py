import discord
from discord.ext import commands

from modules.character import CharacterInfo


class Util(commands.Cog):



    instance: 'Util' = None
    def __init__(self, bot):
        self._user_config_cache = {}
        self.bot = bot
        Util.instance = self
        resp = self.bot.db.execute("PRAGMA table_info(user_config)").fetchall()
        self.user_config_fields = [row["name"] for row in resp if row["name"] != "user_id"]

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

    def get_user_config(self, user_id: int, guild_id: int, config_name: str = None):
        # Try to get the full row from cache
        row = self._user_config_cache.get((user_id, guild_id))
        if row is None:
            row = self.bot.db.execute(
                "SELECT * FROM user_config WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ).fetchone()
            if row:
                self._user_config_cache[(user_id, guild_id)] = row
            else:
                return None

        if config_name is None:
            return row
        if config_name not in self.user_config_fields:
            return None
        return row[config_name]

    def set_user_config(self, user_id: int, guild_id: int, config_name: str, value):
        if config_name not in self.user_config_fields:
            return False
        if isinstance(value, bool):
            value = int(value)
        elif isinstance(value, str):
            if value.lower() == "true":
                value = 1
            elif value.lower() == "false":
                value = 0
        exists = self.bot.db.execute(
            "SELECT 1 FROM user_config WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        ).fetchone()
        if exists:
            self.bot.db.execute(
                f"UPDATE user_config SET {config_name} = ? WHERE user_id = ? AND guild_id = ?",
                (value, user_id, guild_id)
            )
        else:
            self.bot.db.execute(
                f"INSERT INTO user_config (user_id, guild_id, {config_name}) VALUES (?, ?, ?)",
                (user_id, guild_id, value)
            )
        self.bot.connection.commit()
        self._user_config_cache.pop((user_id, guild_id), None)
        return True

    def create_user_config(self, user_id: int, guild_id: int = 0):
        if (user_id, guild_id) in self._user_config_cache:
            return False
        exists = self.bot.db.execute(
            "SELECT 1 FROM user_config WHERE user_id = ? and guild_id = ?",
            (user_id, guild_id)
        ).fetchone()
        if exists:
            return False
        self.bot.db.execute(
            "INSERT INTO user_config (user_id, guild_id) VALUES (?, ?)",
            (user_id, guild_id)
        )
        self._user_config_cache.pop((user_id, guild_id), None)
        return True

    @commands.command()
    async def config(self, context: commands.Context, option: str, value: str):
        if context.guild:
            guild_id = context.guild.id
        else:
            guild_id = 0

        self.create_user_config(context.author.id, guild_id)
        if self.set_user_config(context.author.id, guild_id, option, value):
            await context.send(f"Configuration option `{option}` set to `{value}`.")
        else:
            await context.send(f"Configuration option `{option}` does not exist. Valid options are: " + ", ".join(self.user_config_fields))

async def setup(bot):
    await bot.add_cog(Util(bot))
