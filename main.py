import discord
import asyncio

with open(".token", "r") as file:
    token = file.read()

class Client(discord.Client):
    guild_id = 670551146078928896
    channel_id = 670552115952877582

    async def on_ready(self):
        self.channel = self.get_channel(self.channel_id)
        await self.send_message("Online")

    async def send_message(self, message):
        if self.channel and self.channel.guild.id == self.guild_id:
            await self.channel.send(f"@everyone {message}")

    async def on_message(self, message):
        print(message.content)

client = Client()
client.run(token)




