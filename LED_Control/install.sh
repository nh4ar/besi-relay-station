#!/bin/bash

cp -f ~/besi-relay-station/LED_Control/TurnOffLeds.sh /usr/bin/TurnOffLeds.sh
cp -f ~/besi-relay-station/LED_Control/LEDOff.service /lib/systemd/system/LEDOff.service
chmod +x /usr/bin/TurnOffLeds.sh

systemctl daemon-reload
systemctl enable LEDOff.service
systemctl start LEDOff.service
