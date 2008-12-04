#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: battery
# BEFORE: final interactive
# AFTER: shell_functions
# SECTION: board battery
# MENU: battery
# DESCRIPTION: Verify some battery data
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# get standard test functions
. /etc/test.d/test-functions

# path to the battery parameters

battery_sys=/dev/null
for d in /sys/devices/platform/bq27000-battery.0/power_supply/bat /sys/class/power_supply/battery
do
  [ -e "${d}" ] && battery_sys="${d}" && break
done
[ ! -d "${battery_sys}" ] &&  ABORT no battery found

# voltage is in uV
battery_voltage=$(GET_VALUE "${battery_sys}/voltage_now")

# current is in uA
battery_current=$(GET_VALUE "${battery_sys}/current_now")

# charge in uA/hr (max approx 1.2Ah
battery_charge=$(GET_VALUE "${battery_sys}/charge_full")

# temperature in Celcius * 10
battery_temp=$(GET_VALUE "${battery_sys}/temp")

# display the data
STATUS battery parameters
STATUS voltage = ${battery_voltage} uV
STATUS current = ${battery_current} uA
STATUS charge = ${battery_charge} uA/h
STATUS temperature = ${battery_temp} C*10

# check the values are in range
if [ ${battery_voltage} -lt 2999999 ]
then
  FAIL battery under-voltage
fi
if [ ${battery_temp} -gt 350 ]
then
  FAIL battery overheating
fi
