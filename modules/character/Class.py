import dataclasses


@dataclasses.dataclass
class Class:
    name: str
    level: int
    url: str
    subclass: str = ""
    subclass_url: str = ""

def create_class(data):
    name = data["definition"]["name"]
    level = data["level"]
    url = data["definition"]["moreDetailsUrl"]
    url = url[url.index("/classes")::]
    if "subclassDefinition" not in data or data["subclassDefinition"] is None:
        return Class(name, level, url)
    subclass = data["subclassDefinition"]["name"]
    subclass_url = data["subclassDefinition"]["moreDetailsUrl"][len("/characters")::]
    subclass_url = subclass_url[subclass_url.index("/classes")::]
    return Class(name, level, url, subclass, subclass_url)