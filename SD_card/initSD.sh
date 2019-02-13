#!/bin/bash
mkdir /media/card
mount -v /dev/mmcblk0p1 /media/card
cp ~/besi-relay-station/SD_card/uEnv.txt /media/card/uEnv.txt
sed -i '/mmcblk0p1/ d' /etc/fstab
sed -i '$ a /dev/mmcblk0p1 /media/card auto auto,rw,async,user,nofail 0 0' /etc/fstab
reboot
