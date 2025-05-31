import re

import discord
from discord.ext import commands


async def catalogger(bot: commands.Bot, message: discord.Message) -> tuple[int, int]:
    if not message.embeds or not message.embeds[0].title or not message.embeds[0].title.endswith("deleted"):
        return 0, 0
    embed = message.embeds[0]
    regex = r"ID: (\d+)"
    user_id = 0
    for i in embed.fields:
        if "Sender" in i.name:
            print(i.value)
            user_id = re.search(regex, i.value).group(1)
            break
    if user_id == 0:
        return 0, 0
    print(embed.footer.text)
    result = re.search(regex, embed.footer.text)
    if not result:
        return 0, 0
    message_id = result.group(1)

    return int(message_id), int(user_id)
