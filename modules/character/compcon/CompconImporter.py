import json

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


async def update_character(context: commands.Context, data: str):
    return await import_character(context, data)