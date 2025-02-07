import re

import discord
from discord.ext import commands


async def catalogger(bot: commands.Bot, message: discord.Message) -> tuple[int, int]:
    print(message.embeds[0].title)
    if not message.embeds or not message.embeds[0].title.endswith("deleted"):
        return
    embed = message.embeds[0]
    regex = r"ID: (\d+)"
    user_id = 0
    message_id = 0
    for i in embed.fields:
        if "Sender" in i.name:
            print(i.value)
            user_id = re.search(regex, i.value).group(1)
            break
    if user_id == 0:
        await (bot.get_channel(1336809167633125387)).send(f"Could not find user ID in message {message.id}",
                                                               embed=embed)
    print(embed.footer.text)
    message_id = re.search(regex, embed.footer.text).group(1)
    if message_id == 0:
        await (bot.get_channel(1336809167633125387)).send(f"Could not find message ID in message {message.id}",
                                                               embed=embed)
    return int(message_id), int(user_id)