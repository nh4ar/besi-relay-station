#!/bin/bash
# Bring all wifi interfaces down.
# Identify wifi interfaces as rows from standard output of iwconfig (NOT standard
# error, those are non-wifi interfaces) which start without whitespace.
sleep 30
iwconfig 2> /dev/null | grep -o '^[[:alnum:]]\+' | while read x; do ifdown $x; done
connmanctl disable wifi
# Bring all wifi interfaces up.
sleep 30
iwconfig 2> /dev/null | grep -o '^[[:alnum:]]\+' | while read x; do ifup $x; done
connmanctl enable wifi
