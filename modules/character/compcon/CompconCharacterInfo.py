import datetime
import json
import sqlite3
from typing import override

import discord

from modules.character import CharacterInfo


class CompconCharacterInfo(CharacterInfo):
    def __init__(self, data = None):
        super().__init__()
        if data is None:
            return
        self.name = data["name"] if data else None
        class_str = "No mech active"
        for i in data["mechs"]:
            if i["active"]:
                class_str = f"{i['name']} | {self.parse_frame_name(i["frame"])}\n"
                break
        self.classes = class_str
        self.image = data["cloud_portrait"]
        self.level = f"LL{data["level"]}"
        self.type = "compcon"

        self.callsign = data["callsign"]


    @override
    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"Info for {self.name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{self.owner}>")
        embed.add_field(name="Callsign", value=self.callsign)
        embed.add_field(name="Level", value = f"{self.level}")
        embed.add_field(name="Mech", value = self.classes)

        if self.image:
            embed.set_image(url=self.image)
        return embed

    @staticmethod
    @override
    def from_row(data: sqlite3.Row) -> 'CompconCharacterInfo':
        ret = CompconCharacterInfo()
        CharacterInfo._populate_obj(ret, data)
        return ret

    @staticmethod
    def parse_frame_name(frame_name: str) -> str:
        """
        Parse the frame name into a tuple of (name, model).
        :param frame_name: The frame name to parse.
        :return: A tuple containing the name and model.
        """
        words = frame_name.split('_')
        del words[0]
        return ' '.join(word.capitalize() for word in words)

    @override
    def read_data(self, data):
        data = json.loads(data)
        self.callsign = data["callsign"]
        self.level = data["level"]

    @override
    def write_data(self):
        self.data = json.dumps({
            "callsign": self.callsign,
            "level": self.level
        })
