import discord
from discord.ext import commands
import os
import time as t
import aiohttp
import dotenv
import typing
import pokebase as pb
import asyncio
import aiofiles

dotenv.load_dotenv()


class Client(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='++', intents=discord.Intents.all(), help_command=None, case_insensitive=True, activity=discord.Activity(type=discord.ActivityType.watching, name="over the young trainers."))

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        print(f'Logged in as\n------\n{self.user.name}\n------')
        for cog in os.listdir('./cogs'):
            if cog.endswith('.py'):
                name = cog[:-3]
                try:
                    await self.load_extension(f'cogs.{name}')
                except Exception as e:
                    print(f'Failed to load cog {name}')
                    async with aiofiles.open("runtime_errors.txt", "a") as f:
                        await f.write(t.strftime("%m/%d/%Y, %I:%M") + " || " + str(e) + "\n")
        await self.tree.sync()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(title=f"**Error:** {error}", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            async with aiofiles.open("runtime_errors.txt", "a") as f:
                await f.write(t.strftime("%m/%d/%Y, %I:%M") + " || " + str(error) + "\n")


client = Client()
client.run(os.environ['TOKEN'])

    