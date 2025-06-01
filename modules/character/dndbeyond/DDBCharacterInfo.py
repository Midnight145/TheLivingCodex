import dataclasses
import json
import discord
import datetime

from modules.character.dndbeyond import DDBClass
from modules.character.dndbeyond.CharacterInfo import CharacterInfo


class DDBCharacterInfo(CharacterInfo):
    base_link = "https://www.dndbeyond.com/"

    def __init__(self, data: dict):
        super().__init__()
        self.name = data["name"]
        self.race = data["race"]["fullName"]
        self.classes = []
        tmp = []
        for i in data["classes"]:
            tmp.append(dataclasses.asdict(DDBClass.DDBClass.create_class(i)))
        self.classes = json.dumps(tmp)
        self.image = "https://www.dndbeyond.com/Content/Skins/Waterdeep/images/characters/default-avatar-builder.png"
        if data["decorations"]["avatarUrl"]:
            self.image = data["decorations"]["avatarUrl"].split("?")[0]

    @staticmethod
    def generate_character_embed(character):
        embed = discord.Embed(
            title=f"Info for {character['name']}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{character['owner']}>")
        embed.add_field(name="Link", value=f"[{character['name']}]({character['link']})")
        embed.add_field(name="Race", value=character["race"], inline=False)

        class_str = ""
        classes = json.loads(character["classes"])
        base_str = "{} - [{}]({})"
        base_sub_str = "{} - [{}]({}) | [{}]({})"
        for i in classes:
            if i["subclass"] == "":
                class_str += base_str.format(i["level"], i["name"], DDBCharacterInfo.base_link + i["url"]) + "\n"
            else:
                class_str += base_sub_str.format(i["level"], i["name"], DDBCharacterInfo.base_link + i["url"], i["subclass"],
                                                 DDBCharacterInfo.base_link + i["subclass_url"]) + "\n"

        embed.add_field(name="Class(es)", value=class_str, inline=False)

        embed.set_image(url=character["image"])
        return embed

