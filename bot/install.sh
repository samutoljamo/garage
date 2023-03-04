#!/bin/bash
echo "Installing bot service"

# stop the service
systemctl stop bot.service


# if service file exists, ask if it should be overwritten
if [ -f "/etc/systemd/system/bot.service" ]; then
    echo "Service file already exists. Overwrite? (y/n)"
    read overwrite
    if [ "$overwrite" = "y" ]; then
      # ask for the user of the service
      echo "Enter the user of the service:"
      read user
      sed -i -e "s/{{user}}/$user/g" bot.service

      # ask for the token of the bot
      echo "Enter the token of the bot:"
      read token
      sed -i -e "s/{{token}}/$token/g" bot.service


      # copy the service file to /etc/systemd/system
      cp bot.service /etc/systemd/system/bot.service
    fi
fi

# remove the old directory
rm -rf /opt/garage/bot

# copy files to /opt/garage-bot
mkdir /opt/garage/bot
cp -r * /opt/garage/bot



systemctl daemon-reload
systemctl enable bot.service
systemctl start bot.service