import json

import aiohttp
from discord.ext import commands

from modules.character.pathbuilder import PBCharacterInfo


async def import_character(context: commands.Context, link: str) -> PBCharacterInfo | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=headers) as resp:
            if resp.status != 200:
                await context.send("Failed to fetch character data!")
                return None
            text = await resp.text()
            json_ = json.loads(text)
            if json_["success"]:
                data = json_["build"]
                return PBCharacterInfo(data)


async def update_character(context: commands.Context, link: str):
    ret = await import_character(context, link)
    await context.send("**Not seeing your changes?** Go to `Menu --> Export --> Export JSON` first and reupdate.")
    return ret