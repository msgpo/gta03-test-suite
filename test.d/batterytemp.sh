#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: battery_temp
# BEFORE: final interactive
# AFTER: shell_functions
# SECTION: board battery
# MENU: Tbatt
# DESCRIPTION: Verify some battery data
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# get standard test functions
. /etc/test.d/test-functions

# temperature in Celcius * 10
#battery_temp=$(GET_VALUE /sys/devices/platform/bq27000-battery.0/power_supply/bat/temp)
battery_temp=$(GET_VALUE /sys/class/power_supply/bat/temp)

# display the data
STATUS temperature = ${battery_temp} C*10

# check the value is in range
if [ ${battery_temp} -gt 350 ]
then
  FAIL battery overheating
fi

# a one line way to check
[ ${battery_temp} -lt 50 ] && FAIL battery too cold
