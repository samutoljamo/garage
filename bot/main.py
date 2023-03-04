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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    await ctx.send(s.getsockname()[0])



token = os.environ.get("DISCORD_TOKEN")

if not token:
    print("DISCORD_TOKEN not set, exiting")
    exit()

bot.run(token)