import asyncio
import re

import discord
from discord.ext import commands

from modules.character import CharacterInfo
from modules.character.characters import CharacterModule
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
        Util.instance.create_user_config(message.author.id)

        if not message.content or message.author.id in self.edit_checks or message.guild is None or message.author.bot: return
        prefix = self.bot.db.execute("SELECT prefix FROM config WHERE server_id = ?", (message.guild.id,)).fetchone()[0]
        if message.content[0] == '[' or message.content[0] == prefix:
            return
        if isinstance(message.channel, discord.Thread):
            channel = message.channel.parent
        else:
            channel = message.channel

        char: CharacterInfo = Proxy.instance.handle_proxied_message(message)
        if char is None:
            char, found_prefix = Util.instance.fetch_char_info(message.content, message.author.id)
            if char is None or found_prefix is None:
                return
            full_message = message.content[len(found_prefix):]
        else:
            full_message = message.content

        if len(full_message) == 0:
            await message.delete()
        if self.bot.db.execute("SELECT whitelist_enabled FROM config WHERE server_id = ?", (message.guild.id,)).fetchone()[0] != 0:
            if cooldown := Whitelist.instance.get_channel_cooldown(channel.id, channel.category_id) is None:
                return  # channel is blacklisted
            if Whitelist.instance.get_character_cooldown(char.id, message.channel):
                await message.delete()
                await message.channel.send(f"This character is on cooldown! Please wait {cooldown} seconds")

            await Whitelist.instance.set_cooldown(cooldown, message.channel, char.id)

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
            message: discord.WebhookMessage = await webhook.fetch_message(payload.message_id, thread=channel if thread else discord.utils.MISSING)
        except (discord.NotFound, AttributeError):
            return
        if message.webhook_id != webhook.id:
            return

        # todo: if two characters owned by the same user have the same name, this will grab the first entry instead of the one that matches the message
        # todo: i need to keep a log of messages that are sent by characters and then check that instead of just trying to grab the character by name
        character = self.bot.db.execute("SELECT * FROM characters WHERE name = ? AND owner = ?",
                                        (message.author.display_name, payload.user_id)).fetchone()
        
        if character is None:
            return
        character = CharacterInfo.fetch_character(character["id"])
        if payload.emoji.name == "✖":
            if not payload.user_id == character.owner:
                await message.remove_reaction(payload.emoji, payload.member)
                return
            await message.delete()
            return
        elif payload.emoji.name == "📝":
            if not payload.user_id == character.owner:
                await message.remove_reaction(payload.emoji, payload.member)
                return
            to_delete = await message.channel.send("Enter new message content:")
            try:
                self.edit_checks[payload.member.id] = message
                msg = await self.bot.wait_for("message", check=lambda m: m.author == payload.member and m.guild.id == payload.guild_id and m.channel.id == payload.channel_id, timeout=120)
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
            # todo: add in db what type of character this is
            embed = character.generate_embed()
            await member.send(embed=embed)
            await message.remove_reaction(payload.emoji, payload.member)

        elif payload.emoji.name == "❔":
            member = self.bot.get_user(payload.user_id)
            await member.send(CharacterModule.help_str)
            await member.send(CharacterModule.custom_help_str)
            await member.send(CharacterModule.reaction_help_str)

            await message.remove_reaction(payload.emoji, payload.member)

    # linter thinks kwargs["embed"], thread are type errors because kwargs definition only has str,bool
    # noinspection PyTypeChecker
    @staticmethod
    async def send_message(webhook: discord.Webhook, message: discord.Message, char: CharacterInfo, content: str):
        kwargs = {
            "username": char.name,
            "avatar_url": char.image,
            "content": content,
            "wait": True
        }

        if message.reference is not None:
            message_reference = await message.channel.fetch_message(message.reference.message_id)
            kwargs["embed"] = await create_reply_embed(message_reference)
        if isinstance(message.channel, discord.Thread):
            kwargs["thread"] = message.channel
        await message.delete()
        msg = await webhook.send(**kwargs)
        if Util.instance.get_user_config(message.author.id, "autoreact"):
            await msg.add_reaction("✖")
            await msg.add_reaction("❔")
            await msg.add_reaction("📝")
            await msg.add_reaction("📋")
        print("Adding message " + str(msg.id) + " to cache")
        LogCleanup.cache[message.id] = message.author.id


URL_REGEX = r'https?://\S+'  # Adjust regex as needed


async def create_reply_embed(message: discord.Message):
    jump_link = message.jump_url
    content = ""

    if message.content.strip():
        msg = message.content
        if len(msg) > 100:
            msg = msg[:100]

            if re.search(r'<[at]?[@#:][!&]?(\w+:)?(\d+)?(:[tTdDfFR])?$', msg):
                mention_tail = message.content[100:].split(">")[0]
                if message.content.startswith(msg + mention_tail + ">"):
                    msg += mention_tail + ">"

            if re.search(URL_REGEX, msg):
                msg += message.content[100:].split(" ")[0]
                if len(msg) > 300:
                    msg = re.sub(URL_REGEX, f"*[(very long link removed, click to see original message)]({jump_link})*",
                                 msg)
                msg += " "

            if re.findall(r'\|\|', msg) and re.findall(r'\|\|', message.content):
                if len(re.findall(r'\|\|', msg)) % 2 == 1 and len(re.findall(r'\|\|', message.content)) % 2 == 0:
                    msg += "||"
            if msg != message.content:
                msg += "…"

        content += f"**[Reply to:]({jump_link})** {msg}"
        if message.attachments or message.embeds:
            content += " 📎"
    else:
        content += f"*[(click to see attachment)]({jump_link})*"

    username = message.author.display_name
    avatar_url = message.author.display_avatar.url

    embed = discord.Embed(description=content, color=discord.Color.blue())
    embed.set_author(name=f"{username} ↩", icon_url=avatar_url)

    return embed


async def setup(bot):
    await bot.add_cog(Listeners(bot))