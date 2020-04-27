import discord
import asyncio
import gpiozero
import time
import os
import json
import logging
import Adafruit_DHT as dht
import utils

DHT_PIN = 3
os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open(".token", "r") as file:
    token = file.read()


SETTINGS_FILENAME = "settings.json"
default_settings = {
    "time": 5,
    "debug": False,
}
if not os.path.exists(SETTINGS_FILENAME):
    with open(SETTINGS_FILENAME, "w") as file:
        json.dump(default_settings, file)


class Client(discord.Client):
    guild_id = 670551146078928896
    channel_id = 678990127498002432
    log_channel_id = 678989059217162263
    request_channel_id = 678990230384148481
    
    def __init__(self, button, *args, **kwargs):
        self.button = button
        self.settings = {}
        self._read_settings()
        super().__init__(*args, **kwargs)
        self.timestamp = None
        self.reported = False
        self.channel = None
        self.log_channel = None
        self.request_channel = None
        self.first_start = True
        self.connected = False
        self.bg_task = self.loop.create_task(self.background_task())
        utils.log("Created Client object successfully")

    def _write_settings(self):
        with open(SETTINGS_FILENAME, "w") as file:
            json.dump(self.settings, file)

    def _read_settings(self):
        with open(SETTINGS_FILENAME, "r") as file:
            self.settings = json.load(file)

    async def on_ready(self):
        self.channel = self.get_channel(self.channel_id)
        self.log_channel = self.get_channel(self.log_channel_id)
        self.request_channel = self.get_channel(self.request_channel_id)
        if self.first_start:
            await self.log("Online")
            self.first_start = False
        self.connected = True
        logger.debug("connected to discord")
        if self.channel and self.log_channel and self.request_channel:
            logger.debug("found all required channels")

    async def on_disconnect(self):
        logger.debug("disconnected")
        self.connected = False

    async def log(self, message):
        utils.log(message)
        if self.log_channel and self.log_channel.guild.id == self.guild_id:
            await self.log_channel.send(message)
        
    async def send_important(self, message, everyone=False):
        utils.log("important: " + message)
        if self.channel and self.channel.guild.id == self.guild_id:
            await self.channel.send(f"{'@everyone ' if everyone else ''}{message}")


    async def on_message(self, message):
        utils.log("received message: " + message.content)
        if message.channel.id != self.request_channel_id:
            return
        if message.content.lower().startswith("!lämpötila"):
            await self.temperature()
        
        elif message.content.lower().startswith("!aika"):
            await self.set_time(message.content)

        
        elif message.content.lower().startswith("!debug"):
            split = message.content.split()
            if len(split) < 2:
                return await self.request_channel.send("Jokin meni pieleen! Esimerkki: \"!debug true\"")
            t = split[1]
            try:
                t = utils.to_bool(t)
                if t is None:
                    raise ValueError()
                self.settings['debug'] = t
                await self.log(f"Debug: {t}")
                self._write_settings()
            except ValueError:
                await self.request_channel.send("Jokin meni pieleen! Esimerkki: \"!debug true\"")
    
    async def set_time(self, message):
        split = message.split()
        if len(split) < 2:
            return await self.request_channel.send("Jokin meni pieleen! Esimerkki: \"!aika 5\"")
        t = split[1]
        try:
            t = float(t.replace(",", "."))
            await self.log(f"Time: {t}")
            await self.request_channel.send(f"Hälytän, kun on kulunut {str(t).replace('.', ',')} min")
            self.settings['time'] = t
            self._write_settings()
        except ValueError:
            await self.request_channel.send("Jokin meni pieleen! Esimerkki: \"!aika 5\"")

        

    async def temperature(self):
        """
        Sends the current temperature
        """
        humidity, temperature = dht.read(dht.DHT22, DHT_PIN)
        if temperature:
            await self.request_channel.send(f"{temperature:.1f}")
        else:
            await self.request_channel.send("Jokin meni pieleen")

    async def background_task(self):
        utils.log("waiting until client is ready")
        while not self.connected:
            await asyncio.sleep(1)
        utils.log("background task started")
        while not self.is_closed():
            if self.button.is_pressed:
                utils.log("pressed")
            else:
                utils.log("not pressed")
            if self.timestamp:
                if time.time() - self.timestamp >= self.settings['time'] * 60 :
                    if not self.reported and self.connected:
                        if self.settings['debug']:
                            await self.log(f"Ovi on ollut auki yli {str(self.settings['time']).replace('.', ',')} min")
                        else:
                            await self.send_important(f"Ovi on ollut auki yli {str(self.settings['time']).replace('.', ',')} min")
                        self.reported = True
            await asyncio.sleep(1)
        utils.log("background task terminating")


button = gpiozero.Button(4)
client = Client(button)
client.run(token)




