import dataclasses

@dataclasses.dataclass
class Class:
    name: str
    level: int
    url: str
    subclass: str = ""
    subclass_url: str = ""