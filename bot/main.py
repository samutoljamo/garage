import os
import discord
from discord.ext import commands
import socket

GPIO_INSTALLED = False
try:
    import RPi.GPIO as GPIO
    GPIO_INSTALLED = True
except ImportError:
    print("Warning, RPi.GPIO is not installed")

intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(brief="Returns pong")
async def ping(ctx):
    await ctx.send('pong')

@bot.command(brief="Returns the IP address of the bot in the current network")
async def address(ctx):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    await ctx.send(s.getsockname()[0])

@bot.command(brief="Returns the status of the garage door")
async def status(ctx):
    if not GPIO_INSTALLED:
        await ctx.send("RPi.GPIO is not installed, can't use MagnetSensor")
        return
    if GPIO.input(4):
        await ctx.send("The garage door is open")
    else:
        await ctx.send("The garage door is closed")



token = os.environ.get("DISCORD_TOKEN")

if not token:
    print("DISCORD_TOKEN not set, exiting")
    exit()

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

bot.run(token)