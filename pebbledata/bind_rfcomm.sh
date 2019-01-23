#!/bin/bash

# Pebble1
rfcomm -i hci0 release 0
# CHANGE THIS MAC
rfcomm -i hci0 bind 0 A0:E6:F8:33:74:EC 1
#rfcomm -i hci0 bind 0 00:17:E9:50:60:CF 1
#rfcomm -i hci0 bind 0 00:17:E9:51:E3:17 1
#rfcomm -i hci0 bind 0 00:17:E9:4E:E2:D9 1
#rfcomm -i hci0 bind 0 00:17:EC:4E:93:21 1
#rfcomm -i hci0 bind 0 00:17:E9:4F:F0:55 1

# Pebble2
# rfcomm -i hci1 release 1
# CHANGE THIS MAC
# rfcomm -i hci1 bind 1 00:17:E9:50:60:CF 1
