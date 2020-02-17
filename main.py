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
        while not self.is_closed:
            if self.timestamp:
                if time.time() - self.timestamp >= 10:
                    if not self.reported:
                        self.send_message("Ovi auki yli 5 min")
                        self.reported = True
            await asyncio.sleep(10)



client = Client(command_prefix="!")

def on_press():
    client.reported = False
    client.timestamp = time.time()
    print("pressed")

def on_release():
    client.timestamp = None
    print("released")

button = gpiozero.Button(4, bounce_time=0.2)

button.when_pressed = on_press
button.when_released = on_release
pause()
#client.run(token)




