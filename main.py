import time
import os
import requests
import sys
from sensor import MockSensor, MagnetSensor

SENSOR_PIN = 4 # pin of the button that is pressed when the garage is closed
MOCK = False

# check if debug mode is enabled
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    MOCK = True

if MOCK:
    sensor = MockSensor()
    sensor.set_status(1)
else:
    sensor = MagnetSensor(SENSOR_PIN)

discord_webhook = os.environ.get("DISCORD_WEBHOOK")

if not discord_webhook:
    print("DISCORD_WEBHOOK not set, exiting")
    exit()

timestamp = time.time()
REPORT_DELAY = 5 * 60 # minutes
last_statuses = [9] * 5
status = 0
sent = False

while True:
  try:
      sensor_state = sensor.get_status()
      last_statuses.append(sensor_state)
      if len(last_statuses) > 5:
          last_statuses.pop(0)
      # check if all values are the same
      if all(x == last_statuses[0] for x in last_statuses) and sensor_state != status:
          status = sensor_state
          timestamp = time.time()
          if not status:
              sent = False
      if status and not sent and time.time() - timestamp > REPORT_DELAY:
          requests.post(discord_webhook, json={"content": f"Ovi on ollut auki yli {REPORT_DELAY/60:.2f} min"})
          sent = True
      time.sleep(1)
  except Exception as e:
    print(e)

