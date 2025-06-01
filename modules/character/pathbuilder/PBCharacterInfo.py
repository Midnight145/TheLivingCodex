from modules.character import CharacterInfo

import discord

class PBCharacterInfo(CharacterInfo):

    @staticmethod
    def from_dict(data: dict) -> 'CharacterInfo':
        raise NotImplementedError("This method should be implemented in subclasses.")

    def generate_embed(self) -> discord.Embed:
        raise NotImplementedError("This method should be implemented in subclasses.")