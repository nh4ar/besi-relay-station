#!/bin/bash
rm /etc/network/interfaces
cp ~/besi-relay-station/wifi-services/interfaces /etc/network/interfaces
dos2unix /etc/network/interfaces
ifup wlan0
cd ~/besi-relay-station/wifi-services/wifi-reset
chmod +x install.sh
./install.sh
cd ~/besi-relay-station/wifi-services/wifi-check
chmod +x install.sh
./install.sh
reboot
