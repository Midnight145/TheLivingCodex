import dataclasses

@dataclasses.dataclass
class Class:
    name: str
    level: int
    url: str
    subclass: str = ""
    subclass_url: str = ""

    @staticmethod
    def create_class(data):
        raise NotImplementedError("This method should be implemented in subclasses.")