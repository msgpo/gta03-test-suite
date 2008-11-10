#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# MENU: led1
# Description: Confirm the operation of an LED

# get standard test functions
. /etc/test.d/test-functions

# path to the battery parameters
led=/sys/devices/platform/gta02-led.0/leds:gta02-aux:red/brightness

# check one LED on
SET_VALUE "${led}" 63
OPERATOR_CONFIRM The red LED on

# check one LED off
SET_VALUE "${led}" 0
OPERATOR_CONFIRM The red LED off

