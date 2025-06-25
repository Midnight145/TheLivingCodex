import json
import sqlite3
from typing import override

import discord

from modules.character import CharacterInfo


class DaggerheartCharacterInfo(CharacterInfo):
    def __init__(self, data: dict = None):
        super().__init__()
        self.background = ""
        if data is None:
            return
        with open("daggerheart.json", "w") as f:
            import json
            json.dump(data, f, indent=4)
        char_cache = get_dict_attr(data, "props", "pageProps", "characterCache", "data", "data")
        character = get_dict_attr(data, "props", "pageProps", "characterCache", "character")
        if character is None:
            raise KeyError("Character data not found in provided data.")
        self.name = character["name"]

        self.level = character["level"]
        self.image = character["avatar_url"]
        self.domains = " | ".join(get_dict_attr(char_cache, "character_class_domains", "values"))
        self.subclasses = get_dict_attr(char_cache, "character_subclasses", "values")
        if self.subclasses is None:
            self.subclasses = []
        self.subclasses = " | ".join([i["name"] for i in self.subclasses])

        self.classes = get_dict_attr(char_cache, "character_class_name", "value") + " " + str(self.level)
        # character_class_name

        community = get_dict_attr(char_cache, "character_community", "value", "name")
        ancestry = get_dict_attr(char_cache, "character_ancestry", "value", "name")

        self.race = ""
        if community:
            self.race += community

        if ancestry:
            self.race += " " + ancestry
            self.race = self.race.lstrip()  # if only ancestry is present, remove leading space

    @staticmethod
    @override
    def from_row(data: sqlite3.Row) -> 'DaggerheartCharacterInfo':
        ret = DaggerheartCharacterInfo()
        CharacterInfo._populate_obj(ret, data)
        return ret

    @override
    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"Info for {self.name}",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Player", value=f"<@{self.owner}>")
        embed.add_field(name="Link", value=f"[{self.name}]({self.link})")
        embed.add_field(name="Race", value=self.race, inline=False)
        embed.add_field(name="Class", value=self.classes, inline=False)
        embed.add_field(name="Domains", value=self.domains, inline=False)
        return embed


# todo: generate embed func, write_data, read_data

    @override
    def write_data(self):
        self.data = json.dumps({
            "domains": self.domains
        })

    @override
    def read_data(self, data):
        data = json.loads(data)
        self.domains = data.get("domains", "")


def get_dict_attr(obj, *path_to_key):
    """
    Get a value from a nested dictionary using a path of keys.
    :param obj: The dictionary to search.
    :param path_to_key: The path of keys to follow.
    :return: The value at the specified path, or None if not found.
    """
    for key in path_to_key:
        try:
            obj = obj[key]
        except (KeyError, TypeError):
            return None
    return obj