#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Build a root filesystem from packages
# AUTHOR: Christopher Hall <hsw@openmoko.com>


# This script is just a simple wrapper around opkg that does an
# initial setup so opkg can run.  The script ensures the correct
# options on the opkg command so that packages do not get installed in
# the root of the host system

# defaults

FEED_SECTION_LIST='all armv4t om-gta02'

URL=http://downloads.openmoko.org/repository/testing
#URL="file://${HOME}/oe/build/tmp/deploy/glibc/opk"

OPKG_PROGRAM=/usr/local/openmoko/arm/bin/opkg-cl


# start of script

usage()
{
  [ -n "$1" ] && echo error: $*
  echo
  echo usage: $(basename "$0") '<options>'
  echo '  --url=http://path          where to get the initial package list'
  echo '                             default:' ${URL}
  echo '  --init                     initialise empty root directory (from url)'
  echo '  --list                     show available packages'
  echo '  --list-installed           show packages already installed'
  echo '  --install <packages...>    install some packages'
  echo '  --devices                  create static device files (prefers minimal table)'
  echo '  --devices-normal           prefer normal table (if avaliable)'
  echo '  --remove <packages...>     remove some packages'
  echo '  --tar=archive.tar[.bz2]    create a tar of the rootfs [optional]'
  echo
  echo notes:
  echo '  --init can be used to change the url to a different repository'
  echo '         even after some pachages have been installed'
  echo
  echo examples:
  echo '  '$(basename "$0") --rootfs=/path/to/myroot --init --url=${URL}
  echo '  '$(basename "$0") --rootfs=/path/to/myroot --list
  echo '  '$(basename "$0") --rootfs=/path/to/myroot --install task-openmoko-linux curl ruby
  echo '  '$(basename "$0") --rootfs=/path/to/myroot --devices
  echo '  '$(basename "$0") --rootfs=/path/to/myroot --list-installed
  exit 1
}


# diplay a command an ask for permission to sudo it
# if already under sudo the just run the command
SUDO()
{
  if [ -z "${SUDO_UID}" -o -z "${SUDO_GID}" ]
  then
    echo SUDO: "$@"
    sudo "$@"
  else
    "$@"
  fi
}


makeroot()
{
  local rootfs url
  rootfs="$1"; shift
  url="$1"; shift

  local conf ConfDir
  conf="${rootfs}/etc/opkg.conf"
  ConfDir="${rootfs}/etc/opkg"

  mkdir -p "${rootfs}/etc/opkg"
  mkdir -p "${rootfs}/usr/lib/opkg"

  for item in ${FEED_SECTION_LIST}
  do
    echo src/gz om-dev-${item} "${url}/${item}" > "${ConfDir}/${item}-feed.conf"
  done

  local arch="${ConfDir}/arch.conf"

  # only create the arch.conf if it does not already exist
  if [ ! -e "${arch}" ]
  then
    cat > "${arch}" <<EOF
arch all 1
arch any 6
arch noarch 11
arch arm 16
arch armv4t 21
arch om-gta02 26
EOF
  fi
}
  

# start of main program

[ -x "${OPKG_PROGRAM}" ] || usage unable to locate opkg binary, check installation of Openmoko toolchain


verbose=0
rootfs=/tmp/rootfs
makedevs_dir="$(readlink -f "$(dirname "$0")")/makedevs"
command=null
url="${URL}"
archive=

while [ $# -ne 0 ]
do
  arg="$1"
  case "${arg}" in

    --verbose)
      verbose=1
      ;;
    --rootfs=*)
      rootfs="$(readlink -m "${arg#*=}")"
      ;;
    --url=*)
      url="${arg#*=}"
      ;;
    --tar=*)
      archive="${arg#*=}"
      ;;
    --install)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=install
      ;;
    --dev*-n*)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=devices
      ;;
    --dev*)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=devices-minimal
      ;;
    --remove)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=remove
      ;;
    --configure)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=configure
      ;;
    --init*)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=init
      ;;
    --list)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=list
      ;;
    --list-installed)
      [ X"${command}" = X"null" ] || usage conflicting commands
      command=list_installed
      ;;
    -h|--help)
      usage help message
      ;;
    -*)
      usage invalid argument: ${arg}
      ;;
    *)
      break
      ;;
  esac
  shift
done

echo rootfs = ${rootfs}
echo url = ${url}

[ X"${command}" != X"init" -a ! -d "${rootfs}" ] && usage root directory not inititilaised


# process command
case "${command}" in

  init)
    makeroot "${rootfs}" "${url}"
    SUDO ${OPKG_PROGRAM} -offline "${rootfs}" update
    ;;

  list*)
    ${OPKG_PROGRAM} -offline "${rootfs}" "${command}"
    ;;

  devices*)
    MKDEV=$(make -s -C "${makedevs_dir}" program-name)
    MINIMAL_DEVICE_TABLE=$(make -s -C "${makedevs_dir}" device-table-name)
    INTERNAL_DEVICE_TABLE="${rootfs}/etc/device_table"

    case "${command}" in
      devices-minimal)
        device_table="${MINIMAL_DEVICE_TABLE}"
        ;;
      *)
        device_table=${INTERNAL_DEVICE_TABLE}
        ;;
    esac

    if [ ! -x "${MKDEV}" ]
    then
      make -C "${makedevs_dir}" all
    fi

    if [ ! -f "${device_table}" ]
    then
      if [ -f "${MINIMAL_DEVICE_TABLE}" ]
      then
        device_table="${MINIMAL_DEVICE_TABLE}"
      elif [ -f "${INTERNAL_DEVICE_TABLE}" ]
      then
        device_table="${INTERNAL_DEVICE_TABLE}"
      else
        usage internal error: no device tables found
      fi
    fi

    echo using program: ${MKDEV}
    echo using device table: ${device_table}

    SUDO rm -f "${rootfs}/dev/"*
    SUDO ${MKDEV}  --root="${rootfs}" --devtable="${device_table}"
    # --squash           Squash permissions and owners making all files be owned by root
    ;;

  install)
    SUDO ${OPKG_PROGRAM} -offline "${rootfs}" update

    for item in "$@"
    do
      SUDO ${OPKG_PROGRAM} -offline "${rootfs}" -force-reinstall -force-defaults install "${item}"
    done
    ;;

  remove|configure)
    for item in "$@"
    do
      SUDO ${OPKG_PROGRAM} -offline "${rootfs}" "${command}" "${item}"
    done
    ;;

  null)
    [ -z "${archive}" ] && usage no command has been specified
    ;;

  *)
    usage unsupported command: ${command}
    ;;
esac

if [ -n "${archive}" ]
then
  echo creating archive of the root file system: ${archive}

  local flag=

  [ X"${archive}" != X"${archive%.bz2}" ] && flag=j
  [ X"${archive}" != X"${archive%.gz}" ] && flag=z

  tar -c${flag}f "${archive}" -C "${rootfs}" .
  [ -n "${SUDO_UID}" -a -n "${SUDO_GID}" ] && chown "${SUDO_UID}:${SUDO_GID}" "${archive}"

fi
