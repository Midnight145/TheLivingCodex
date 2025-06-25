import dataclasses
import datetime
import sqlite3
from typing import TypeVar, Type

import discord

from LivingCodex import LivingCodex
from modules.character import Class

ExtendsCharacterInfo = TypeVar("ExtendsCharacterInfo", bound='CharacterInfo')

@dataclasses.dataclass
class CharacterInfo:
    id: int = 0
    name: str = ""
    race: str = ""
    classes: str | list[Class] = ""  # string or list of Class objects
    image: str = ""
    owner: int = 0
    link: str = ""
    subclass: str = ""
    subclass_url: str = ""
    backstory: str = ""
    type: str = ""
    data: str = ""

    @staticmethod
    def fetch_character(cid: int) -> ExtendsCharacterInfo:
        """Fetch character information from the database."""
        resp = LivingCodex.instance.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        type_ = CharacterInfo.__get_charinfo_class(resp["type"])
        character = type_.from_row(resp)
        character.read_data(resp["data"])
        return character

    @staticmethod
    def from_row(data: sqlite3.Row) -> ExtendsCharacterInfo:
        ret = CharacterInfo()
        CharacterInfo._populate_obj(ret, data)
        return ret

    @staticmethod
    def _populate_obj(obj: ExtendsCharacterInfo, data: sqlite3.Row):
        """
        Populate a character info object from a database row. Should not be overridden in subclasses.
        :param obj:
        :param data:
        :return:
        """
        obj.id = data["id"]
        obj.name = data["name"]
        obj.race = data["race"]
        obj.classes = data["classes"]
        obj.image = data["image"]
        obj.backstory = data["backstory"]
        obj.owner = data["owner"]
        obj.link = data["link"]
        obj.type = data["type"]
        obj.data = data["data"]
        obj.read_data(data["data"])

    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"Info for {self.name}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Player", value=f"<@{self.owner}>")
        if self.image:
            embed.set_image(url=self.image)
        return embed

    def write_character(self, db, create = False):
        self.write_data()
        if create:
            db.execute(
                "INSERT INTO characters (name, owner, backstory, race, classes, image, link, type, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.name, self.owner, self.backstory, self.race, self.classes,
                 self.image, self.link, self.type, self.data))
        else:
            db.execute("UPDATE characters SET id = ?, name = ?, race = ?, classes = ?, image = ?, backstory = ?, owner = ?, link = ?, type = ?, data = ? WHERE id = ?",
                   (self.id,
                    self.name,
                    self.race,
                    self.classes if isinstance(self.classes, str) else dataclasses.asdict(self.classes),
                    self.image,
                    self.backstory,
                    self.owner,
                    self.link,
                    self.type,
                    self.data,
                    self.id
                    ))

    def read_data(self, data):
        """
        Read data into the character info object.
        This should be overridden in subclasses if they have additional data to read.
        Called after the object is created from the database.
        :param data: The custom data read from the database.
        """
        self.data = data

    def write_data(self):
        """
        Write data from the character info object.
        This should be overridden in subclasses if they have additional data to write.
        Called before the object is saved to the database.
        """
        pass

    @staticmethod
    def __get_charinfo_class(string: str) -> Type[ExtendsCharacterInfo]:
        from modules.character import ModuleDefinitions
        if string in ModuleDefinitions.modules:
            return ModuleDefinitions.modules[string].charinfo
        raise ValueError(f"Unknown character type: {string}")