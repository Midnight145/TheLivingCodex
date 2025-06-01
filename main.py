import sqlite3
import sys
import traceback

import discord

from LivingCodex import LivingCodex
from modules.errorhandler import TracebackHandler


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

with open('token.txt', 'r') as token:
    TOKEN = token.read().rstrip()


async def get_prefix(bot_, message):
    list_ = [bot_.user.mention + " "]
    if message.guild is None:
        list_.append(">")
    else:
        list_.append(
            bot_.db.execute("SELECT prefix FROM config WHERE server_id = ?", (message.guild.id,)).fetchone()[0])
    return list_

connection = sqlite3.connect("chars.db", check_same_thread=False)
connection.row_factory = sqlite3.Row

db = connection.cursor()
db.execute("CREATE TABLE IF NOT EXISTS config (server_id INTEGER PRIMARY KEY, startup_channel INTEGER, whitelist_enabled BOOLEAN, prefix TEXT DEFAULT '>', log_cleanup_enabled BOOLEAN DEFAULT FALSE)")

intents = discord.Intents.all()

bot = LivingCodex(db, connection, command_prefix=get_prefix, intents=intents, help_command=None)
LivingCodex.instance = bot


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