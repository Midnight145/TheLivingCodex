import dataclasses
from typing import TypeVar, Type

from modules.character import CharacterInfo
from modules.character.compcon import CompconImporter, CompconCharacterInfo
from modules.character.dndbeyond import DDBImporter, DDBCharacterInfo
from modules.character.pathbuilder import PBImporter, PBCharacterInfo
from modules.character.scoundry import ScoundryImporter, ScoundryCharacterInfo

ExtendsCharacterInfo = TypeVar("ExtendsCharacterInfo", bound=CharacterInfo)

@dataclasses.dataclass
class Module:
    type: str
    importer: callable
    updater: callable
    charinfo: Type[ExtendsCharacterInfo]

modules = {
    "ddb": Module("ddb", DDBImporter.import_character, DDBImporter.update_character, DDBCharacterInfo),
    "pb": Module("pb", PBImporter.import_character, PBImporter.update_character, PBCharacterInfo),
    "scoundry": Module("scoundry", ScoundryImporter.import_character, ScoundryImporter.update_character, ScoundryCharacterInfo),
    "compcon": Module("compcon", CompconImporter.import_character, CompconImporter.update_character, CompconCharacterInfo),
    "custom": Module("custom", None, None, CharacterInfo)
}

def fetch_import_method(link: str) -> Module | None:
    if "dndbeyond.com" in link:
        return modules["ddb"]
    if "pathbuilder2e.com" in link:
        return modules["pb"]
    if "scoundry.com" in link:
        return modules["scoundry"]
    if "compcon.app" in link:
        return modules["compcon"]
    return None