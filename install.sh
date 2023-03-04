#/bin/bash

cp garage.service /etc/systemd/system/garage.service

systemctl daemon-reload
systemctl enable garage.service
systemctl start garage.service