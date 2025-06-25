from discord.ext import commands
import aiohttp

from modules.character.daggerheart.CustomHTMLParser import CustomHTMLParser
from modules.character.daggerheart.DaggerheartCharacterInfo import DaggerheartCharacterInfo


async def import_character(context: commands.Context, link: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=headers) as resp:
            if resp.status != 200:
                await context.send("Failed to fetch character data!")
                return None
            data = await resp.text()

    parser = CustomHTMLParser()
    parser.feed(data)
    json_ = parser.get_json()
    if not json_:
        await context.send("Failed to parse character data!")
        return
    try:
        return DaggerheartCharacterInfo(json_)
    except ValueError as e:
        await context.send(f"Error parsing character data: {e}")
        return None

async def update_character(context: commands.Context, link: str):
    return await import_character(context, link)