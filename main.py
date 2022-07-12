import discord
from discord.ext import commands
import os
import time as t
import aiohttp
import dotenv
import typing
import asyncio
import aiofiles
import utils
import pokemoon as pm

dotenv.load_dotenv()


class Client(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='pm!', intents=discord.Intents.all(), help_command=None, case_insensitive=True, activity=discord.Activity(type=discord.ActivityType.watching, name="over the young trainers."))

    async def setup_hook(self):
        print(f'Logged in as\n------\n{self.user.name}\n------')
        for cog in os.listdir('./cogs'):
            if cog.endswith('.py'):
                name: str = cog[:-3]
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
            embed: discord.Embed = discord.Embed(title=f"**Error:** {error}", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            async with aiofiles.open("runtime_errors.txt", "a") as f:
                await f.write(t.strftime("%m/%d/%Y, %I:%M") + " || " + str(error) + "\n")

client = Client()

@client.command(name='help', aliases=[], help='Shows this message.', usage='[command=None]')
async def _help(ctx, command=None):
    if command is None:
        embed: discord.Embed = discord.Embed(title="Help", color=discord.Color.blue(), description=f"Welcome to the Pokemoon discord bot. Use {ctx.prefix}help [command] to get more information about a command.")
        embed.add_field(name="OR", value="You can use this select menu to help you navigate the categories provided", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name} | Not Implemented", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        embed: discord.Embed = discord.Embed(title=f"Help for {command.title()}", color=discord.Color.blue(), description=(command:=client.get_command(command)).help)
        embed.add_field(name="Usage", value=f"`{ctx.prefix}[{'|'.join(alias for alias in [command.name, *command.aliases])}] {command.usage}`", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name} | Not Implemented", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

@client.command(name='invite', aliases=[], help='Invite the bot to your server.', usage='')
async def invite(ctx):
    embed: discord.Embed = discord.Embed(title="Invite Link", color=discord.Color.blue(), description=f"Use [this](https://discordapp.com/api/oauth2/authorize?client_id=994124767361773648&permissions=8&scope=bot%20applications.commands) link to invite the bot to your server!")
    embed.set_footer(text=f"Requested by {ctx.author.name} | Not Implemented", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed, view=utils.Link(name="Invite the bot", url="https://discord.com/api/oauth2/authorize?client_id=994124767361773648&permissions=8&scope=bot%20applications.commands"))
       
@client.command(name='pokedex', aliases=['dex'], help='Get information about a pokemon. You can set details to "detailed" to get more info on a pokemon.', usage='<pokemon> [details=default]')
async def pokedex(ctx: commands.Context, pokemon: str | int | None, *, detailed: str | None = "default"):
    # pokemon = await pm.pokemon(pokemon)
    # embed = discord.Embed(title=f"{pokemon.name}", color=discord.Color.blue())
    async with client.session.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}/") as resp:
        data: asyncio.coroutine = await resp.json()
        embed: discord.Embed = discord.Embed(title=f"#{'0' * (3 - len(str(data['id']))) + str(data['id'])} - {data['name'].title()}", color=discord.Color.blue())
        embed.set_thumbnail(url=data['sprites']['other']['official-artwork']['front_default'])
        if "detailed" == detailed.lower():
            embed.add_field(name="Types", value=", ".join([x['type']['name'].title() for x in data['types']]))
            embed.add_field(name="Height", value=f"{data['height'] / 10}m")
            embed.add_field(name="Weight", value=f"{data['weight'] / 10}kg")
            embed.add_field(name="Abilities", value=", ".join([ability['ability']['name'].title() for ability in data['abilities']]), inline=False)
            embed.add_field(name="Stats", value="\n".join([f"**{stat['stat']['name'].title()}**: {stat['base_stat']}" for stat in data['stats']]), inline=False)
            return await ctx.send(embed=embed)
        embed.add_field(name="Types", value=", ".join([x['type']['name'].title() for x in data['types']]))
        embed.add_field(name="Stats", value="\n".join([f"**{x['stat']['name'].replace('-', ' ').title()}**: {x['base_stat']}" for x in data['stats']]), inline=False)
    await ctx.send(embed=embed)

@client.command(name='test', aliases=['t'], help='Test command.', usage='<command>')
async def test(ctx: commands.Context, command: str):
    command = client.get_command(command)
    await ctx.send(f"The command, {command.name} has the following aliases: {command.aliases}")

async def main():
    async with client:
        client.session: aiohttp.ClientSession = aiohttp.ClientSession()
        await client.start(os.environ['TOKEN'])

asyncio.run(main())
    