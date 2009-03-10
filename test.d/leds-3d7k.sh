#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: leds
# BEFORE: final
# AFTER: shell_functions interactive
# SECTION: led interactive 3d7k
# MENU: LEDs
# DESCRIPTION: Confirm the operation of the LEDs
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# get standard test functions
. /etc/test.d/test-functions

# path to the LED parameters
led_sys=/sys/devices/platform/s3c2440-i2c.0/i2c-adapter:i2c-0/0-0032

INFO using: ${led_sys}

# leds
#colours='red green blue'
colours='green blue'

enable='_enable'
pwm='_pwm'
current='_cur'

off='disable'
on='direct'

nominal_current=8
minimum_pwm=0
maximum_pwm=255

# set all LEDs off
AllOff()
{
  local led
  for led in ${colours}
  do
    SET_VALUE "${led_sys}/${led}${current}" 0
    SET_VALUE "${led_sys}/${led}${pwm}" 0
    SET_VALUE "${led_sys}/${led}${enable}" "${off}"
  done
}

# flash LED
FLASH()
{
  local led brightness v inc
  led="$1"; shift
  brightness="${led_sys}/${led}${pwm}" 0
  SET_VALUE "${led_sys}/${led}${enable}" "${on}"
  SET_VALUE "${led_sys}/${led}${current}" "${nominal_current}"
  v=0
  inc=1
  while :
  do
    SET_VALUE "${brightness}" "${v}"
    v=$((${v} + ${inc}))
    [ ${v} -ge ${maximum_pwm} ] && inc=$((0 - ${inc}))
    [ ${v} -le ${minimum_pwm} ] && inc=$((0 - ${inc}))
  done
}

# ask the operator to confirm
AllOff
OPERATOR_CONFIRM All LEDs are off

# loop to check each LED
for led in ${colours}
do
  AllOff
  FLASH "${led}" &
  pid="$!"
  OPERATOR_CONFIRM The ${colour} LED is flashing
  kill "${pid}"
  sleep 1
  kill -9 "${pid}"
done

# ask the operator to confirm
AllOff
OPERATOR_CONFIRM All LEDs are off
