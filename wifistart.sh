#!/bin/bash
cd ~/besi-relay-station/wifi-services/wifi-reset
chmod +x install.sh
./install.sh
connmanctl tether wifi off
connmanctl disable wifi
connmanctl enable wifi
connmanctl scan wifi
connmanctl services
connmanctl agent on
connmanctl connect wifi_e0b94d199709_424553495f524f55544552_managed_none
reboot
