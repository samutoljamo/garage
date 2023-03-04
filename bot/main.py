import os
import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

intents = discord.Intents.default()
intents.message_content = True

token = os.environ.get("DISCORD_TOKEN")

if not token:
    print("DISCORD_TOKEN not set, exiting")
    exit()

client = MyClient(intents=intents)
client.run(token)