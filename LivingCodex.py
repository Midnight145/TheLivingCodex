import sqlite3

from discord.ext import commands


class LivingCodex(commands.Bot):
    instance: 'LivingCodex' = None

    def __init__(self, db: sqlite3.Cursor, connection: sqlite3.Connection, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.connection = connection
        self.all_cogs, self.loaded_cogs, self.unloaded_cogs = [], [], []
        self.COG_FILE = "COGS.txt"
        self.traceback = {}

        with open(self.COG_FILE, "r") as cogs:
            self.all_cogs = [i.rstrip() for i in cogs.readlines()]
