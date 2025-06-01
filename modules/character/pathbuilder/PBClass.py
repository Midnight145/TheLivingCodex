from modules.character import Class


class PBClass(Class):
    @staticmethod
    def create_class(data):
        name = data["definition"]["name"]
        level = data["level"]
        url = data["definition"]["moreDetailsUrl"]
        if "/classes" in url:
            url = url[url.index("/classes")::]
        if "subclassDefinition" not in data or data["subclassDefinition"] is None:
            return PBClass(name, level, url)
        subclass = data["subclassDefinition"]["name"]
        subclass_url = data["subclassDefinition"]["moreDetailsUrl"]
        subclass_url = subclass_url[subclass_url.index("/classes")::]
        return PBClass(name, level, url, subclass, subclass_url)