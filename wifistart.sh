#!/bin/bash
cd ~/besi-relay-station/wifi-services/wifi-reset
chmod +x install.sh
./install.sh
connmanctl tether wifi off
connmanctl disable wifi
connmanctl enable wifi
connmanctl scan wifi
connmanctl services
