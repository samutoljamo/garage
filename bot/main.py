import os
import discord
from discord.ext import commands
import socket

intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def address(ctx):
    await ctx.send(socket.gethostbyname(socket.gethostname()+".local"))



token = os.environ.get("DISCORD_TOKEN")

if not token:
    print("DISCORD_TOKEN not set, exiting")
    exit()

bot.run(token)