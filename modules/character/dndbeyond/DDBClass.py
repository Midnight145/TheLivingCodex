import dataclasses

from modules.character import Class


@dataclasses.dataclass
class DDBClass(Class):
    @staticmethod
    def create_class(data):
        name = data["definition"]["name"]
        level = data["level"]
        url = data["definition"]["moreDetailsUrl"]
        if "/classes" in url:
            url = url[url.index("/classes")::]
        if "subclassDefinition" not in data or data["subclassDefinition"] is None:
            return DDBClass(name, level, url)
        subclass = data["subclassDefinition"]["name"]
        subclass_url = data["subclassDefinition"]["moreDetailsUrl"]
        subclass_url = subclass_url[subclass_url.index("/classes")::]
        return DDBClass(name, level, url, subclass, subclass_url)
