import datetime
import sqlite3
from typing import override

import discord

from modules.character import CharacterInfo


class ScoundryCharacterInfo(CharacterInfo):
    def __init__(self, data = None):
        super().__init__()
        if data is None:
            return
        self.name = data["name"] if data else None
        self.classes = data["playbook"]
        self.image = data["portrait"]

        # scoundry doesn't really have a "race" so we use alias instead here
        self.alias = data["alias"]

    @override
    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"Info for {self.name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{self.owner}>")
        embed.add_field(name="Alias", value=self.alias, inline=False)
        embed.add_field(name="Playbook", value = self.classes.capitalize())
        if self.image:
            embed.set_image(url=self.image)
        return embed

    @staticmethod
    @override
    def from_row(data: sqlite3.Row) -> 'ScoundryCharacterInfo':
        ret = ScoundryCharacterInfo()
        CharacterInfo._populate_obj(ret, data)
        return ret

    @override
    def read_data(self, data):
        self.alias = data

    @override
    def write_data(self):
        self.data = self.alias