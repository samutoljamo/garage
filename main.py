import asyncio
import time
import os
import traceback
import json

import discord
# import gpio
import RPi.GPIO as GPIO


import utils

time.sleep(10)  # give some time for rasp pi to start

DHT_PIN = 3  # data pin of temperature sensor
SENSOR_PIN = 4 # pin of the button that is pressed when the garage is closed

# read discord token
os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open(".token", "r") as file:
    token = file.read()


# if settings file doesn't exist, create it and fill it with default values
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
    role_id = 760413534453628939

    def __init__(self, sensor_pin, *args, **kwargs):
        self.sensor_pin = sensor_pin
        self.settings = {}
        self._read_settings()
        super().__init__(*args, **kwargs)
        self.channel = None
        self.log_channel = None
        self.request_channel = None
        self.first_start = True
        self.bg_task = self.loop.create_task(self.background_task())
        self.ok_emoji = '🆗'
        self.state = {
            "open": False,
            "reported": False,
            "timestamp": None,
            "sent_message": None,
        }
        utils.log("Created Client object successfully")

    def _write_settings(self):
        # save settings from memory to disk
        with open(SETTINGS_FILENAME, "w") as file:
            json.dump(self.settings, file)

    def _read_settings(self):
        # load settigns from disk to memory
        with open(SETTINGS_FILENAME, "r") as file:
            self.settings = json.load(file)

    async def on_ready(self):
        self.channel = self.get_channel(self.channel_id)
        self.log_channel = self.get_channel(self.log_channel_id)
        self.request_channel = self.get_channel(self.request_channel_id)
        if self.first_start: # to prevent spam when connection is weak
            await self.log("Online")
            self.first_start = False
        utils.log("connected to discord")
        if self.channel and self.log_channel and self.request_channel:
            utils.log("found all required channels")

    async def on_disconnect(self):
        utils.log("disconnected")

    async def log(self, message):
        # logs to disk, stdout and discord log channel
        utils.log(message)
        if self.log_channel:
            return await self.log_channel.send(message)

    async def send_important(self, message):
        # send a message to channel which creates a notification for the members
        utils.log("important: " + message)
        if self.channel and self.channel.guild.id == self.guild_id:
            return await self.channel.send(f"<@&{self.role_id}> {message}")

    async def on_message(self, message):
        utils.log("received message: " + message.content)
        if message.channel.id != self.request_channel_id:
            return

        elif message.content.lower().startswith("!aika"):
            await self.set_time(message.content)
        
        elif message.content.lower().startswith("!status"):
            if self.state['open']:
                await self.request_channel.send(f"Ovi on ollut auki {(time.time() - self.state['timestamp'])/60:.2f} min")
            else:
                await self.request_channel.send("Ovi on suljettu")

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
    
    async def send_state(self):
        message = None
        if self.settings['debug']:
            message = await self.log(f"Ovi on ollut auki yli {str(self.settings['time']).replace('.', ',')} min")
        else:
            message = await self.send_important(f"Ovi on ollut auki yli {str(self.settings['time']).replace('.', ',')} min")
        self.state['reported'] = True
        self.state['sent_message'] = message

    async def background_task(self):
        """
        asyncronous loop that checks every second if the garage door is opened or closed.
        if it is open for too long(time is specified by user) it will notify the user through discord
        """
        utils.log("waiting until client is ready")
        await asyncio.sleep(10)
        utils.log("background task started")
        previous_values = []
        while not self.is_closed():
            try:
                sensor_state = GPIO.input(self.sensor_pin)
                previous_values.append(sensor_state)
                if len(previous_values) > 5:
                    previous_values.pop(0)
                # check if all values are the same
                if all(x == previous_values[0] for x in previous_values):
                    if sensor_state == GPIO.LOW:
                        if self.state['open'] == False:
                            self.state['open'] = True
                            self.state['timestamp'] = time.time()
                            await self.log("garage door opened")
                        else:
                            if time.time() - self.state['timestamp'] > self.settings['time'] * 60 and not self.state['reported']:
                                await self.send_state()
                    else:
                        if self.state['open'] == True:
                            self.state['open'] = False
                            self.state['timestamp'] = None
                            self.state['reported'] = False
                            await self.log("garage door closed")

                        # if message exists, add a reaction to it and delete it from state
                        if self.state['sent_message']:
                            await self.state['sent_message'].add_reaction(self.ok_emoji)
                            self.state['sent_message'] = None

            except Exception as e:
                utils.log(' '.join(traceback.format_exception(
                    etype=type(e), value=e, tb=e.__traceback__)))
            finally:
                await asyncio.sleep(1)
        utils.log("background task terminating")
        os.system("sudo reboot")


GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
client = Client(SENSOR_PIN)
try:
    client.run(token)
finally:
    GPIO.cleanup()
