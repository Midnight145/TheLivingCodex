import base64
import binascii
import json
import re

from discord.ext import commands

from modules.character.scoundry import ScoundryCharacterInfo


async def import_character(context: commands.Context, link: str) -> ScoundryCharacterInfo | None:
    regex = r"^(https?://)?(www\.)?scoundry\.com/import/(?P<b64>[A-Za-z0-9\-_]+={0,2}).*"
    match = re.match(regex, link)
    encoded = match.group("b64") if match else None
    # python will strip any extra padding, but will error if it doesn't have enough so we add more to be safe
    encoded += "=="
    print(encoded)
    if not encoded:
        await context.send("Invalid Scoundry link! Please provide a valid import link. Example: https://scoundry.com/import/.....")
        return None

    try:
        decoded = base64.b64decode(encoded).decode()
        print(decoded)
        json_ = json.loads(decoded)
    except binascii.Error:
        await context.send("Failed to decode the base64 data! Please check the link.")
        return None
    except json.JSONDecodeError:
        await context.send("Invalid JSON data received! Please check the link.")
        return None
    return ScoundryCharacterInfo(json_)


async def update_character(context: commands.Context, link: str):
    return await import_character(context, link)