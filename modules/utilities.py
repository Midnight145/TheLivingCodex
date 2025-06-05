import datetime

import discord
from discord.ext import commands


# noinspection DuplicatedCode
class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["kill", "stop"])
    @commands.is_owner()
    async def die(self, context):
        await context.send("Bot shutting down...")
        self.bot.db.close()
        await self.bot.close()

    @commands.command(aliases=['ul'])
    @commands.is_owner()
    async def unload(self, context, arg):
        if arg not in self.bot.all_cogs:
            arg = "modules." + arg
        if arg not in self.bot.all_cogs:
            await context.send(f"Error: cog {arg} doesn't exist. Check spelling or capitalization.")
            return
        if arg in self.bot.unloaded_cogs:
            await context.send(f"Cog {arg} already unloaded! Try loading it first.")
            return
        await self.bot.unload_extension(arg)
        await context.send(f"Cog {arg} successfully unloaded!")
        self.bot.loaded_cogs.remove(arg)
        self.bot.unloaded_cogs.append(arg)

    @commands.command(aliases=['l'])
    @commands.is_owner()
    async def load(self, context, arg):
        if arg not in self.bot.all_cogs:
            arg = "modules." + arg
        if arg not in self.bot.all_cogs:
            await context.send(f"Error: cog {arg} doesn't exist. Check spelling or capitalization.")
            return
        if arg in self.bot.loaded_cogs:
            await context.send(f"Cog {arg} already loaded! Try unloading it first.")
            return
        await self.bot.load_extension(arg)
        await context.send(f"Cog {arg} successfully loaded!")
        self.bot.unloaded_cogs.remove(arg)
        self.bot.loaded_cogs.append(arg)

    @commands.command(aliases=['rl'])
    @commands.is_owner()
    async def reload_cog(self, context, arg):
        if arg not in self.bot.all_cogs:
            arg = "modules." + arg
        if arg not in self.bot.all_cogs:
            await context.send(f"Error: cog {arg} doesn't exist. Check spelling or capitalization.")
            return
        if arg in self.bot.unloaded_cogs:
            await context.send(f"Cog {arg} is unloaded, loading instead.")
            await self.bot.load_extension(arg)
            await context.send(f"Cog {arg} successfully loaded!")
            self.bot.unloaded_cogs.remove(arg)
            self.bot.loaded_cogs.append(arg)
            return
        await self.bot.reload_extension(arg)
        await context.send(f"Cog {arg} successfully reloaded!")

    @commands.command(name="reload", aliases=["r"], hidden=True)
    @commands.is_owner()
    async def reload_all(self, ctx: commands.Context):
        """Reloads all cogs"""
        for cog in self.bot.all_cogs:
            try:
                await self.bot.unload_extension(cog)
                await self.bot.load_extension(cog)
                self.bot.loaded_cogs.append(cog)
                self.bot.unloaded_cogs.remove(cog)
            except Exception as e:
                self.bot.traceback[cog] = e
                self.bot.unloaded_cogs.append(cog)
                self.bot.loaded_cogs.remove(cog)
        await ctx.send("Reloaded all cogs")

    @commands.command()
    @commands.is_owner()
    async def rename(self, context, *, name):
        await self.bot.user.edit(username=name)
        await context.send("Username successfully changed!")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def set_prefix(self, context, prefix):
        self.bot.db.execute("UPDATE config SET prefix = ? WHERE server_id = ?", (prefix, context.guild.id))
        self.bot.connection.commit()
        await context.send(f"Prefix successfully changed to {prefix}")

    @commands.command()
    async def botinfo(self, context):
        creator = await self.bot.fetch_user(self.bot.owner_id)
        embed = discord.Embed(
            title="Bot Info",
            description="",
            color=discord.Color.gold()
        )
        embed.set_author(name="Created by " + str(creator), icon_url=creator.display_avatar.url)
        embed.set_thumbnail(url=creator.display_avatar.url)
        embed.set_image(url=self.bot.user.display_avatar.url)
        embed.add_field(name="User ID", value=self.bot.user.id, inline=False)
        embed.add_field(name="Join Date",
                        value=context.guild.get_member(self.bot.user.id).joined_at.strftime("%Y-%m-%d %H:%M.%S"),
                        inline=False)
        embed.add_field(name="Other Info", value="Created with discord.py", inline=False)
        await context.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def execute(self, context, *, query):
        resp = self.bot.db.execute(query).fetchall()
        self.bot.connection.commit()
        await context.send(f"Query processed. Rows found: {len(resp)}")

    @commands.command()
    @commands.is_owner()
    async def add_cog(self, context: commands.Context, arg):
        if arg not in self.bot.all_cogs:
            self.bot.all_cogs.append(arg)
            with open(self.bot.COG_FILE, "a") as cogs:
                cogs.write(arg + "\n")
            await context.send(f"Cog {arg} successfully added!")
        else:
            await context.send(f"Cog {arg} already seems to exist, not adding.")

    @commands.command()
    @commands.is_owner()
    async def delete_cog(self, context: commands.Context, arg):
        if arg in self.bot.all_cogs:
            self.bot.all_cogs.remove(arg)

            with open(self.bot.COG_FILE, "w") as cogs:
                cogs.writelines([i + "\n" for i in self.bot.all_cogs])
            await context.send(f"Cog {arg} successfully deleted!")
        else:
            await context.send(f"Cog {arg} does not exist, not deleting.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, context: commands.Context, limit=None):
        await context.message.delete()

        if limit is None:
            check = lambda x: x.author == self.bot.user
        else:
            check = lambda x: True
        await context.channel.purge(limit=int(limit) if limit is not None else 100, check=check)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def message(self, context, member: discord.Member, *, contents: str):
        files = [(await i.to_file()) for i in context.message.attachments]

        embed = discord.Embed(
            title=f"New Message",
            description=contents,
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        await context.send("Message sent!")
        try:
            await member.send(embed=embed, files=files)
        except discord.Forbidden:
            await context.send(f"Error in sending message to {member.mention}: Forbidden")

    @commands.command()
    async def id(self, context: commands.Context, member: discord.Member = None):
        if member is None:
            member = context.author
        await context.send(str(member.id))

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def inrole(self, context: commands.Context, role: discord.Role):
        to_send = f"Members in role {role.name}:\n"
        for member in role.members:
            to_send += str(member) + f"  ({member.display_name})\n"

        await context.send(to_send)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if guild.id not in self.bot.config:
            self.bot.db.execute("INSERT INTO config (server_id) VALUES (?)", (guild.id,))
            self.bot.connection.commit()

async def setup(bot):
    await bot.add_cog(Utilities(bot))
