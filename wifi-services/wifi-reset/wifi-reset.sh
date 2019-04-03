#!/bin/bash
# Bring all wifi interfaces down.
# Identify wifi interfaces as rows from standard output of iwconfig (NOT standard
# error, those are non-wifi interfaces) which start without whitespace.
sleep 30
connmanctl disable wifi
iwconfig 2> /dev/null | grep -o '^[[:alnum:]]\+' | while read x; do ifdown $x; done
# Bring all wifi interfaces up.
sleep 30
connmanctl enable wifi
iwconfig 2> /dev/null | grep -o '^[[:alnum:]]\+' | while read x; do ifup $x; done

