import asyncio

import discord
from discord.ext import commands

from modules.character.proxy import Proxy
from modules.character.util import Util
from modules.character.whitelist import Whitelist
from modules.character.logclean import LogCleanup


class Listeners(commands.Cog):
    # noinspection PyTypeChecker
    def __init__(self, bot):
        self.bot = bot
        self.edit_checks = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.content or message.author.id in self.edit_checks or message.guild is None or message.author.bot: return
        prefix = self.bot.db.execute("SELECT prefix FROM config WHERE server_id = ?", (message.guild.id,)).fetchone()[0]
        if message.content[0] == '[' or message.content[0] == prefix:
            return
        if isinstance(message.channel, discord.Thread):
            channel = message.channel.parent
        else:
            channel = message.channel

        char = Proxy.instance.handle_proxied_message(message)
        if char is None:
            char, found_prefix = Util.instance.fetch_char_info(message.content, message.author.id)
            if char is None or found_prefix is None:
                return
            full_message = message.content[len(found_prefix['prefix']):]
        else:
            full_message = message.content

        if len(full_message) == 0:
            await message.delete()
        if self.bot.db.execute("SELECT whitelist_enabled FROM config WHERE server_id = ?", (message.guild.id,)).fetchone()[0] != 0:
            if cooldown := Whitelist.instance.get_channel_cooldown(channel.id, channel.category_id) is None:
                return  # channel is blacklisted
            if Whitelist.instance.get_character_cooldown(char["id"], message.channel):
                await message.delete()
                await message.channel.send(f"This character is on cooldown! Please wait {cooldown} seconds")

            await Whitelist.instance.set_cooldown(cooldown, message.channel, char["id"])

        webhook = await Util.instance.create_webhook(channel)
        await self.send_message(webhook, message, char, full_message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if isinstance(channel, discord.Thread):
            true_channel = channel.parent
            thread = True
        else:
            true_channel = channel
            thread = False
        if channel.guild is None:
            return

        webhook = None
        try:
            webhooks = await true_channel.webhooks()
        except discord.Forbidden:
            await channel.send("Error: Webhook permissions denied, check the channel or role settings.")
            return
        for i in webhooks:
            if i.user.id == self.bot.user.id:
                webhook = i
                break
        try:
            message = await webhook.fetch_message(payload.message_id, thread=channel if thread else discord.utils.MISSING)
        except (discord.NotFound, AttributeError):
            return
        if message.webhook_id != webhook.id:
            return
        message: discord.WebhookMessage

        character = self.bot.db.execute("SELECT * FROM characters WHERE name = ?",
                                        (message.author.display_name,)).fetchone()
        if character is None:
            return
        if payload.emoji.name == "✖":
            if not payload.user_id == character["owner"]:
                await message.remove_reaction(payload.emoji, payload.member)
                return
            await message.delete()
            return
        elif payload.emoji.name == "📝":
            if not payload.user_id == character["owner"]:
                await message.remove_reaction(payload.emoji, payload.member)
                return
            to_delete = await message.channel.send("Enter new message content:")
            try:
                self.edit_checks[payload.member.id] = message
                msg = await self.bot.wait_for("message", check=lambda m: m.author == payload.member, timeout=120)
                await message.edit(content=msg.content)
                await msg.delete()
            except asyncio.TimeoutError:
                await message.channel.send("Timed out!")
            finally:
                del self.edit_checks[payload.member.id]
                await to_delete.delete()
                await message.remove_reaction(payload.emoji, payload.member)

        elif payload.emoji.name == "📋":
            member = self.bot.get_user(payload.user_id)
            await message.remove_reaction(payload.emoji, member)
            embed = Util.generate_character_embed(character)
            await member.send(embed=embed)
            await message.remove_reaction(payload.emoji, payload.member)

        elif payload.emoji.name == "❔":
            member = self.bot.get_user(payload.user_id)
            await member.send(Util.help_str)

            await message.remove_reaction(payload.emoji, payload.member)

    @staticmethod
    async def send_message(webhook: discord.Webhook, message: discord.Message, char: dict, content: str):
        kwargs = {
            "username": char["name"],
            "avatar_url": char["image"],
            "content": content,
            "wait": True
        }

        if message.reference is not None:
            message_reference = await message.channel.fetch_message(message.reference.message_id)
            jump_url = message_reference.jump_url
            kwargs["content"] += f"\n\n[Replied message]({jump_url})"
        if isinstance(message.channel, discord.Thread):
            kwargs["thread"] = message.channel
        await message.delete()
        msg = await webhook.send(**kwargs)
        await msg.add_reaction("✖")
        await msg.add_reaction("❔")
        await msg.add_reaction("📝")
        await msg.add_reaction("📋")
        print("Adding message " + str(msg.id) + " to cache")
        LogCleanup.cache[message.id] = message.author.id


async def setup(bot):
    await bot.add_cog(Listeners(bot))