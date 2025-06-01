import dataclasses

import discord

from LivingCodex import LivingCodex
from modules.character.dndbeyond.DDBCharacterInfo import DDBCharacterInfo

@dataclasses.dataclass
class CharacterInfo:
    id: int
    name: str
    race: str
    classes: str | list[str]  # string or list of class names
    image: str
    owner: str
    link: str = ""
    subclass: str = ""
    subclass_url: str = ""
    backstory: str = ""

    @staticmethod
    def fetch_character(cid: int) -> 'CharacterInfo':
        """Fetch character information from the database."""
        resp = LivingCodex.instance.db.execute("SELECT * FROM characters WHERE id = ?", (cid,)).fetchone()
        type_ = resp["type"]
        match type_:
            case "ddb":
                return DDBCharacterInfo.from_dict(resp)
            case _:
                raise ValueError(f"Unknown character type: {type_}")

    @staticmethod
    def from_dict(data: dict) -> 'CharacterInfo':
        raise NotImplementedError("This method should be implemented in subclasses.")

    def generate_embed(self) -> discord.Embed:
        raise NotImplementedError("This method should be implemented in subclasses.")