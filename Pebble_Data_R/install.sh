#!/bin/bash

ntpdate -b -s -u pool.ntp.org

# install dependencies
sudo pip install libpebble2
sudo apt-get install python-zmq
sudo pip install msgpack-python
sudo pip install redis
sudo pip install supervisor

cp ~/besi-relay-station/Pebble_Data_R/supervisord.service /etc/systemd/system/supervisord.service

# install supervisor config
mkdir /etc/supervisor
cp ~/besi-relay-station/Pebble_Data_R/supervisord.conf /etc/supervisor/supervisord.conf

# enable supervisord.service
systemctl enable supervisord.service
systemctl start supervisord.service
