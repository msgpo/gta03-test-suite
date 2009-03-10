#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: leds
# BEFORE: final
# AFTER: shell_functions interactive
# SECTION: led interactive gta02
# MENU: LEDs(02)
# DESCRIPTION: Confirm the operation of the LEDs
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# get standard test functions
. /etc/test.d/test-functions

# path to the LED parameters
led_sys=/sys/devices/platform/gta02-led.0/leds

INFO using: ${led_sys}

# leds
red="${led_sys}:gta02-aux:red/brightness"
blue="${led_sys}:gta02-power:blue/brightness"
orange="${led_sys}:gta02-power:orange/brightness"

# set all LEDs off
AllOff()
{
  SET_VALUE "${red}" 0
  SET_VALUE "${blue}" 0
  SET_VALUE "${orange}" 0
}

# ask the operator to confirm
AllOff
OPERATOR_CONFIRM All LEDs are off

# loop to check each LED
for colour in red blue orange
do
  AllOff
  eval led="\${${colour}}"
  SET_VALUE "${led}" 63
  OPERATOR_CONFIRM The ${colour} LED on
done

# ask the operator to confirm
AllOff
OPERATOR_CONFIRM All LEDs are off
