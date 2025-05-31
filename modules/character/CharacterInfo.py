import dataclasses
import json

from modules.character import Class


class CharacterInfo:

    def __init__(self, data: dict):
        self.name = data["name"]
        self.race = data["race"]["fullName"]
        self.backstory = data["notes"]["backstory"]
        self.classes = []
        tmp = []
        for i in data["classes"]:
            tmp.append(dataclasses.asdict(Class.create_class(i)))
        self.classes = json.dumps(tmp)
        self.image = "https://www.dndbeyond.com/Content/Skins/Waterdeep/images/characters/default-avatar-builder.png"
        if data["decorations"]["avatarUrl"]:
            self.image = data["decorations"]["avatarUrl"].split("?")[0]