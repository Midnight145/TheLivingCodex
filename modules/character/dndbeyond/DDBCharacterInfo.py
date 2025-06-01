import dataclasses
import json
import sqlite3

import discord
import datetime

from modules.character.dndbeyond import DDBClass
from modules.character import CharacterInfo


class DDBCharacterInfo(CharacterInfo):
    base_link = "https://www.dndbeyond.com/"

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.name = data["name"]
        self.race = data["race"]["fullName"]
        self.classes = []
        tmp = []
        for i in data["classes"]:
            tmp.append(dataclasses.asdict(DDBClass.create_class(i)))
        self.classes = json.dumps(tmp)
        self.image = "https://www.dndbeyond.com/Content/Skins/Waterdeep/images/characters/default-avatar-builder.png"
        if data["decorations"]["avatarUrl"]:
            self.image = data["decorations"]["avatarUrl"].split("?")[0]

    def __blank_ctor(self):
        pass

    def generate_character_embed(self):
        embed = discord.Embed(
            title=f"Info for {self.name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{self.owner}>")
        embed.add_field(name="Link", value=f"[{self.name}]({self.link})")
        embed.add_field(name="Race", value=self.race, inline=False)

        class_str = ""
        classes = json.loads(self.classes)
        base_str = "{} - [{}]({})"
        base_sub_str = "{} - [{}]({}) | [{}]({})"
        for i in classes:
            if i["subclass"] == "":
                class_str += base_str.format(i["level"], i["name"], DDBCharacterInfo.base_link + i["url"]) + "\n"
            else:
                class_str += base_sub_str.format(i["level"], i["name"], DDBCharacterInfo.base_link + i["url"], i["subclass"],
                                                 DDBCharacterInfo.base_link + i["subclass_url"]) + "\n"

        embed.add_field(name="Class(es)", value=class_str, inline=False)

        embed.set_image(url=self.image)
        return embed

    @staticmethod
    def from_row(data: sqlite3.Row) -> 'DDBCharacterInfo':
        """
        Create a DDBCharacterInfo instance from a dictionary pulled from the database.
        :param data: The data from the database
        :return: The created DDBCharacterInfo instance
        """
        ret = DDBCharacterInfo()
        ret.id = data["id"]
        ret.name = data["name"]
        ret.race = data["race"]
        ret.classes = data["classes"]
        ret.image = data["image"]
        ret.backstory = data["backstory"]
        ret.owner = data["owner"]
        ret.link = data["link"]
        if data["subclass"] is not None:
            ret.subclass = data["subclass"]
        if data["subclass_url"] is not None:
            ret.subclass_url = data["subclass_url"]
            
        return ret