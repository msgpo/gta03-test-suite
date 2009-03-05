#!/bin/sh
# Bluetooth ethernet connection

PowerOff()
{
  echo 0 > /sys/bus/platform/devices/neo1973-pm-bt.0/reset
  echo 0 > /sys/bus/platform/devices/neo1973-pm-bt.0/power_on
}


PowerOn()
{
  # ensure off
  PowerOff

  # power on
  sleep 1
  echo 1 > /sys/bus/platform/devices/neo1973-pm-bt.0/power_on
  sleep 1

  # reset
  echo 1 > /sys/bus/platform/devices/neo1973-pm-bt.0/reset
  echo 0 > /sys/bus/platform/devices/neo1973-pm-bt.0/reset
  sleep 2

  # force a rescan of the USB in case we have just been resumed
  lsusb -v > /dev/null
}

connect()
{
  local name mac_addr
  name="$1"; shift
  mac_addr="$1"; shift

  echo -n Connecting to: ${name} = ${mac_addr}
  count=15
  while [ "${count}" -gt 0 ]
  do
    count=$((${count} - 1))
    echo -n .
    pand --connect "${mac_addr}" --service NAP --autozap
    sleep 2
    if pand --show | grep -q bnep0
    then
      echo OK
      return 0
    fi
  done
  echo Failed
  return 1
}


start()
{
  local mac_addr name junk flag count

  echo Starting Bluetooth
  PowerOn

  hcitool scan | (
    while read mac_addr name junk
    do
      case "${name}" in
        mac-*|hsw-*)
          if connect "${name}" "${mac_addr}"
          then
            exit 0
          fi
          ;;
        ...)
          ;;
        *)
          echo ignore: ${name} = ${mac_addr}
          ;;
      esac
    done
    exit 1
    )
  if [ $? -ne 0 ]
  then
    echo Connection failed: no matching remote device name
    stop
  fi
}

stop()
{
  echo Stopping Bluetooth
  pand --killall
  PowerOff
}

status()
{
  hciconfig
  pand --show
  ifconfig bnep0
}


# main program
case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart|reload)
    stop && sleep 2 && start
    ;;
  status)
    status
    ;;
  *)
    echo "Usage: $(basename "$0") {start|stop|restart|reload|status}"
    ;;
esac
