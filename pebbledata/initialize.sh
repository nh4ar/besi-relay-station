#!/bin/bash


# setup programs
# echo "--- Setting up pebbledata ---"
# chmod +x state_monitor.py
chmod +x bind_rfcomm.sh

# update device name
echo "--- Updating Bluetooth Device Name ---"
read -p "Enter a name for the bluetooth adapter: " bluename
echo "Naming device ${bluename}"
echo "PRETTY_HOSTNAME=${bluename}" > /etc/machine-info
service bluetooth restart

