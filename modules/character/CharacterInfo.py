import dataclasses
import sqlite3

import discord

from LivingCodex import LivingCodex
from modules.character import Class


@dataclasses.dataclass
class CharacterInfo:

    id: int = 0
    name: str = ""
    race: str = ""
    classes: str | list[Class] = ""  # string or list of Class objects
    image: str = ""
    owner: str = 0
    link: str = ""
    subclass: str = ""
    subclass_url: str = ""
    backstory: str = ""
    type: str = ""

    @staticmethod
    def fetch_character(cid: int) -> 'CharacterInfo':
        """Fetch character information from the database."""
        resp = LivingCodex.instance.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        type_ = resp["type"]
        match type_:
            case "ddb":
                from modules.character.dndbeyond import DDBCharacterInfo
                return DDBCharacterInfo.from_row(resp)
            case "pb":
                from modules.character.pathbuilder.PBCharacterInfo import PBCharacterInfo
                return PBCharacterInfo.from_row(resp)
            case "custom":
                return CharacterInfo.from_row(resp)
            case _:
                raise ValueError(f"Unknown character type: {type_}")

    @staticmethod
    def from_row(data: sqlite3.Row) -> 'CharacterInfo':
        ret = CharacterInfo()
        CharacterInfo._populate_obj(ret, data)
        return ret

    @staticmethod
    def _populate_obj(obj: 'CharacterInfo', data: sqlite3.Row):
        obj.id = data["id"]
        obj.name = data["name"]
        obj.race = data["race"]
        obj.classes = data["classes"]
        obj.image = data["image"]
        obj.backstory = data["backstory"]
        obj.owner = data["owner"]
        obj.link = data["link"]
        obj.type = data["type"]

    def generate_embed(self) -> discord.Embed:
        raise NotImplementedError("This method should be implemented in subclasses.")

    def write_character(self, db):
        db.execute("UPDATE characters SET id = ?, name = ?, race = ?, classes = ?, image = ?, backstory = ?, owner = ?, link = ?, type = ? WHERE id = ?",
                   (self.id,
                    self.name,
                    self.race,
                    self.classes if isinstance(self.classes, str) else dataclasses.asdict(self.classes),
                    self.image,
                    self.backstory,
                    self.owner,
                    self.link,
                    self.type,
                    self.id
                    ))