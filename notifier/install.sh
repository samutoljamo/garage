#!/bin/bash
echo "Installing notifier service"

# stop the service
systemctl stop notifier.service


# if service file exists, ask if it should be overwritten
if [ -f "/etc/systemd/system/notifier.service" ]; then
    echo "Service file already exists. Overwrite? (y/n)"
    read overwrite
    if [ "$overwrite" = "y" ]; then
      # ask for the user of the service
      echo "Enter the user of the service:"
      read user
      sed -i -e "s/{{user}}/$user/g" notifier.service

      # ask for the webhook url
      echo "Enter the webhook url:"
      read webhook
      sed -i -e "s/{{discord_webhook}}/$webhook/g" notifier.service


      # copy the service file to /etc/systemd/system
      cp notifier.service /etc/systemd/system/notifier.service
    fi
fi

# remove the old directory
rm -rf /opt/garage/notifier

# copy files to /opt/garage-bot
mkdir /opt/garage/notifier
cp -r * /opt/garage/notifier



systemctl daemon-reload
systemctl enable notifier.service
systemctl start notifier.service