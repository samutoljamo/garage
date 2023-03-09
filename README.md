# garage
A discord bot that notifies you when you left your garage door open for too long
This is currently running on a raspberry zero w connected to a hall effect sensor

## Services
I divided the task into two independent services which are configured as linux services:
1. Notifier - sends a message via webhook api if the garage door is open for too long.
2. Bot - responds to commands like !status which tells if door is open or closed
It's a bit confusing since they appear as two different bots but it simplified the notifier service
## Configuration
1. Make sure you have python with rpi.gpio installed
2. Clone the repo
3. Install other requirements from requirements.txt
4. run `sudo sh install.sh` in repo root
   - You will need webhook url, token of the bot and the user used for running linux services(usually it's pi)



