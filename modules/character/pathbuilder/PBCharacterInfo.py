import sqlite3
from typing import override

from modules.character import CharacterInfo

import datetime
import discord

class PBCharacterInfo(CharacterInfo):

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.name = data["name"]
        self.classes = data["class"]
        for i in data["feats"]:
            feat_name: str = i[0]
            if feat_name.endswith("Dedication"):
                feat_name = feat_name[:-11]
                self.classes += f" | {feat_name}"
        self.race = data["ancestry"] + " | " + data["heritage"]

    @override
    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"Info for {self.name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{self.owner}>")
        embed.add_field(name="Race", value=self.race, inline=False)
        embed.add_field(name="Class", value = self.classes)
        if self.image:
            embed.set_image(url=self.image)
        return embed

    @staticmethod
    @override
    def from_row(data: sqlite3.Row) -> 'CharacterInfo':
        ret = PBCharacterInfo()
        CharacterInfo._populate_obj(ret, data)
        ret.type = "pb"
        return ret