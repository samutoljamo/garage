#!/bin/bash

# stop the service
systemctl stop bot.service

# remove the old directory
rm -rf /opt/garage/bot

# copy files to /opt/garage-bot
cp -r * /opt/garage/bot

# copy the service file to /etc/systemd/system
cp bot.service /etc/systemd/system/bot.service

systemctl daemon-reload
systemctl enable bot.service
systemctl start bot.service