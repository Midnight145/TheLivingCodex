import dataclasses

@dataclasses.dataclass
class CharacterInfo:
    name: str
    race: str
    classes: str | list[str]  # string or list of class names
    image: str
    backstory: str = ""
