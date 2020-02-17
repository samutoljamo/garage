import discord
import asyncio
import gpiozero
import time
from signal import pause


with open(".token", "r") as file:
    token = file.read()


class Client(discord.Client):
    guild_id = 670551146078928896
    channel_id = 670552115952877582
    timestamp = None
    reported = False


    async def on_ready(self):
        self.channel = self.get_channel(self.channel_id)
        await self.send_message("Online")

    async def send_message(self, message, everyone=False):
        if self.channel and self.channel.guild.id == self.guild_id:
            await self.channel.send(f"{'@everyone ' if everyone else ''}{message}")


    async def on_message(self, message):
        if message.channel.id != self.channel_id:
            return
        if message.content.startswith("!lämpötila"):
            await self.temperature()

    async def temperature(self):
        """
        Sends the current temperature
        """
        await self.send_message("23")

    async def background_task(self):
        await self.wait_until_ready()
        print("Background task started")
        print(self.is_closed)
        while not self.is_closed:
            print(self.timestamp)
            if self.timestamp:
                print(time.time() - self.timestamp)
                if time.time() - self.timestamp >= 10:
                    if not self.reported:
                        self.send_message("Ovi auki yli 5 min")
                        self.reported = True
            await asyncio.sleep(1)



client = Client(command_prefix="!")

def on_press():
    client.timestamp = None
def on_release():
    print("Released")
    client.reported = False
    client.timestamp = time.time()

button = gpiozero.Button(4)

button.when_pressed = on_press
button.when_released = on_release
client.loop.create_task(client.background_task())
client.run(token)




