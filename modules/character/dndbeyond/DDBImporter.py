import re

import aiohttp
from discord.ext import commands

from modules.character.dndbeyond import DDBCharacterInfo

async def import_character(context: commands.Context, link: str) -> DDBCharacterInfo | None:
    """
    Import a character from D&D Beyond using the provided link.

    Args:
        link (str): The URL of the D&D Beyond character.

    Returns:
        str: A message indicating the result of the import operation.
        :param context: the command invocation context
        :param link: the D&D Beyond character link
    """
    ddb_api = "https://character-service.dndbeyond.com/character/v5/character/"
    char_id = __fetch_cid_from_link(link)
    if char_id == -1:
        await context.send("Invalid link!")
        return None
    link = ddb_api + str(char_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status == 403:
                await context.send(
                    f"Failed to fetch character data! Make sure your character is set to public [here](https://www.dndbeyond.com/characters/{char_id}/builder/home/basic)")
                return None
            if resp.status != 200:
                await context.send("Failed to fetch character data!")
                return None
            data = (await resp.json())["data"]
    return DDBCharacterInfo(data)


async def update_character(context: commands.Context, link: str):
    return await import_character(context, link)

def __fetch_cid_from_link(link: str) -> int:
    regex = r"^(https?:\/\/)?www\.dndbeyond\.com\/characters\/(?P<id>\d+).*"
    char_id = re.match(regex, link)
    if char_id is None:
        return -1
    else:
        return int(char_id.group("id"))