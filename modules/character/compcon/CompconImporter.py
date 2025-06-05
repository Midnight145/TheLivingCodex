import json

import aiohttp
from discord.ext import commands

from modules.character.compcon.CompconCharacterInfo import CompconCharacterInfo


async def import_character(context: commands.Context, data: str) -> CompconCharacterInfo | None:
    await context.send("Importing Compcon character...")
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        await context.send("Invalid JSON data received! Please check the input.")
        return None
    return CompconCharacterInfo(data)


async def update_character(context: commands.Context, link: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status != 200:
                await context.send("Failed to fetch character data!")
                return None
            data = await resp.text()
    return await import_character(context, data)