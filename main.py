import os
import sqlite3
import sys
import traceback
from sqlite3 import Connection

import discord

from LivingCodex import LivingCodex
from modules.errorhandler import TracebackHandler

import load_dotenv

env = load_dotenv.load_dotenv()

DB_FILE = os.getenv("DATABASE_FILE")
if DB_FILE is None:
    raise EnvironmentError("DATABASE_FILE environment variable is not set.")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init_db() -> Connection:
    connection = sqlite3.connect(DB_FILE, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    db.execute("CREATE TABLE IF NOT EXISTS config (server_id INTEGER PRIMARY KEY, startup_channel INTEGER DEFAULT 0, whitelist_enabled BOOLEAN DEFAULT FALSE, prefix TEXT DEFAULT '>', log_clean_enabled BOOLEAN DEFAULT FALSE)")
    db.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY, whitelisted BOOLEAN DEFAULT FALSE, cooldown INTEGER DEFAULT 0, type TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS characters (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, race TEXT, classes TEXT, image TEXT, backstory TEXT, link TEXT, owner INTEGER, type TEXT, data TEXT DEFAULT '')")
    db.execute("CREATE TABLE IF NOT EXISTS prefixes (id INTEGER PRIMARY KEY, cid INTEGER, prefix TEXT, owner INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS proxies (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cid INTEGER, channel INTEGER, thread INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS user_config (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, guild_id INTEGER NOT NULL DEFAULT 0, autoreact BOOLEAN DEFAULT FALSE)")

    return connection

TOKEN = os.getenv("DISCORD_TOKEN")


connection = init_db()
db = connection.cursor()

async def get_prefix(bot_, message):
    list_ = [bot_.user.mention + " "]
    if message.guild is None:
        list_.append(">")
    else:
        list_.append(bot_.db.execute("SELECT prefix FROM config WHERE server_id = ?", (message.guild.id,)).fetchone()[0])

    return list_

intents = discord.Intents.all()

bot = LivingCodex(db, connection, command_prefix=get_prefix, intents=intents, help_command=None)
LivingCodex.instance = bot
bot.get_custom_prefix = get_prefix

@bot.event
async def on_ready():
    print("Logged in")
    for i in bot.all_cogs:
        print("Loading " + i)
        if i in bot.loaded_cogs: continue
        await bot.load_extension(i)
        bot.loaded_cogs.append(i)
    print("All cogs loaded successfully!")
    # noinspection PyTypeChecker
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Rolling for initiative!"))


# noinspection PyUnusedLocal
@bot.event
async def on_error(event, *args, **kwargs):
    exc_type, exc_name, exc_traceback = sys.exc_info()
    traceback.print_exc()
    channel = bot.get_channel(1336809167633125387)
    err_code = 255
    for i in range(len(bot.traceback) + 1):
        if i in bot.traceback:
            continue
        err_code = i
    original = getattr(exc_traceback, '__cause__', exc_traceback)
    handler = TracebackHandler(err_code, f"{exc_type.__name__}: {str(exc_name)}", original)
    bot.traceback[err_code] = handler
    await channel.send(f"An error occurred in {event}. Error code: {str(err_code)}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    db.execute("INSERT INTO config (server_id) VALUES (?)", (guild.id,))
    connection.commit()

bot.run(TOKEN)