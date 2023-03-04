#!/bin/bash

# stop the service
systemctl stop notifier.service

# remove the old directory
rm -rf /opt/garage/notifier

# copy files to /opt/garage-bot
cp -r * /opt/garage/notifier

# copy the service file to /etc/systemd/system
cp notifier.service /etc/systemd/system/garage.service

systemctl daemon-reload
systemctl enable notifier.service
systemctl start notifier.service