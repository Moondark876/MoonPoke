import discord
from discord.ext import commands
import os
import time as t
import aiohttp
import dotenv
import typing
import utils

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
                    with open("runtime_errors.txt", "a") as f:
                        f.write(t.strftime("%m/%d/%Y, %I:%M") + " || " + str(e) + "\n")
        await self.tree.sync()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(title=f"**Error:** {error}", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            with open("runtime_errors.txt", "a") as f:
                f.write(t.strftime("%m/%d/%Y, %I:%M") + " || " + str(error) + "\n")


client = Client()

@client.command()
async def types(ctx):
    embed = discord.Embed(title="Types", color=discord.Color.blue(), description="{}".format(',\n'.join(f"**{i.title()}**" for i in utils.Type.__members__)))
    await ctx.send(embed=embed)

@client.command()
async def type(ctx, *, type: utils.TypeCheck):
    embed = discord.Embed(title=f"{type.name.title()}-types", color=discord.Color.blue())
    embed.add_field(name="Weak", value=', '.join(type.weak) or None, inline=False)
    embed.add_field(name="Neutral", value=', '.join(type.neutral) or None, inline=False)
    embed.add_field(name="Resist", value=', '.join(type.resist) or None, inline=False)
    embed.add_field(name="Immune", value=', '.join(type.immune) or None, inline=False)
    await ctx.send(embed=embed)
    
client.run(os.environ['TOKEN'])
#test

    