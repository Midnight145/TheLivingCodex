import dataclasses
import json
import sqlite3
from typing import override

import discord
import datetime

from modules.character.dndbeyond.DDBClass import DDBClass
from modules.character import CharacterInfo, Class


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


    @override
    def generate_embed(self):
        embed = discord.Embed(
            title=f"Info for {self.name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{self.owner}>")
        embed.add_field(name="Link", value=f"[{self.name}]({self.link})")
        embed.add_field(name="Race", value=self.race, inline=False)

        class_str = ""
        # classes = json.loads(self.classes)
        base_str = "{} - [{}]({})"
        base_sub_str = "{} - [{}]({}) | [{}]({})"

        for i in self.classes:
            i: DDBClass
            if i.subclass == "":
                class_str += base_str.format(i.level, i.name, DDBCharacterInfo.base_link + i.url) + "\n"
            else:
                class_str += base_sub_str.format(i.level, i.name, DDBCharacterInfo.base_link + i.url, i.subclass,
                                                 DDBCharacterInfo.base_link + i.subclass_url) + "\n"

        embed.add_field(name="Class(es)", value=class_str, inline=False)

        embed.set_image(url=self.image)
        return embed

    @staticmethod
    @override
    def from_row(data: sqlite3.Row) -> 'DDBCharacterInfo':
        """
        Create a DDBCharacterInfo instance from a dictionary pulled from the database.
        :param data: The data from the database
        :return: The created DDBCharacterInfo instance
        """

        ret = DDBCharacterInfo()
        CharacterInfo._populate_obj(ret, data)
        ret.classes = []
        classes = json.loads(data["classes"])
        for i in classes:
            ret.classes.append(DDBClass(
                level=i["level"],
                name=i["name"],
                url=DDBCharacterInfo.base_link + i["url"],
                subclass=i["subclass"],
                subclass_url=DDBCharacterInfo.base_link + i["subclass_url"]
            ))
            
        return ret