import discord
import asyncio
import gpiozero
import time
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open(".token", "r") as file:
    token = file.read()


class Client(discord.Client):
    guild_id = 670551146078928896
    channel_id = 678990127498002432
    log_channel_id = 678989059217162263
    request_channel_id = 678990230384148481
    timestamp = None
    reported = False
    max_time_open = 5
    channel = None
    log_channel = None
    request_channel = None
    


    async def on_ready(self):
        self.channel = self.get_channel(self.channel_id)
        self.log_channel = self.get_channel(self.log_channel_id)
        self.request_channel = self.get_channel(self.request_channel_id)

        await self.log("Online")

    async def log(self, message):
        if self.log_channel and self.log_channel.guild.id == self.guild_id:
            await self.log_channel.send(message)
        
    async def send_important(self, message, everyone=False):
        if self.channel and self.channel.guild.id == self.guild_id:
            await self.channel.send(f"{'@everyone ' if everyone else ''}{message}")


    async def on_message(self, message):
        if message.channel.id != self.request_channel_id:
            return
        if message.content.startswith("!lämpötila"):
            await self.temperature()
        
        elif message.content.startswith("!aika"):
            await self.set_time(message.content)
    
    async def set_time(self, message):
        split = message.split()
        if len(split) < 2:
            await self.request_channel.send("Jokin meni pieleen! Esimerkki: \"!aika 5\"")
        t = split[1]
        try:
            t = float(t.replace(",", "."))
            self.max_time_open = t
        except ValueError:
            await self.request_channel.send("Jokin meni pieleen! Esimerkki: \"!aika 5\"")

        

    async def temperature(self):
        """
        Sends the current temperature
        """
        await self.request_channel.send("23")

    async def background_task(self):
        await self.wait_until_ready()
        while not self.log_channel:
            await asyncio.sleep(1)
        await self.log("Background task started")
        while not self.is_closed():
            if self.timestamp:
                if time.time() - self.timestamp >= self.max_time_open * 60:
                    if not self.reported:
                        await self.send_important(f"Ovi on ollut auki yli {str(self.max_time_open).replace('.', ',')} min")
                        self.reported = True
            await asyncio.sleep(1)



client = Client()

def on_press():
    client.timestamp = None

def on_release():
    client.reported = False
    client.timestamp = time.time()

button = gpiozero.Button(4)
if not button.is_pressed:
    on_release()
button.when_pressed = on_press
button.when_released = on_release
client.loop.create_task(client.background_task())
client.run(token)




