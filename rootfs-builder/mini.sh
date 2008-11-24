#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Build a minimal image for gta02
# AUTHOR: Christopher Hall <hsw@openmoko.com>


# normalise the path names
ThisDirectory="$(readlink -m "$(dirname "$0")")"

ROOT_BUILDER="${ThisDirectory}/rootfs-builder.sh"

# a subdirectory called 'restricted' where this script is located
# contains the binaries that overide the system ones
# It is very bad to have /bin and /usr/bin here, but the 'postinst'
# scripts are shell scripts so need access to all the utilities
# Just DO NOT sudo this
RESTRICTED_PATH="${ThisDirectory}/restricted:/bin:/usr/bin"


usage()
{
  [ -n "$1" ] && echo error: $*
  echo
  echo usage: $(basename "$0") '/path/to/rootfs [/path/to/cache]'
  exit 1
}

RBLD()
{
  local rc=0
  if [ -n "${CacheDirectory}" ]
  then
    ${ROOT_BUILDER} --rootfs="${RootfsDirectory}" --path="${RESTRICTED_PATH}" --cache="${CacheDirectory}" "$@"
    rc="$?"
  else
    ${ROOT_BUILDER} --rootfs="${RootfsDirectory}" --path="${RESTRICTED_PATH}" "$@"
    rc="$?"
  fi

  [ "${rc}" -ne 0 ] && usage Rooot Builder script failed
}


# main program

RootfsDirectory="$1"; shift
CacheDirectory="$1"; shift

[ -z "${RootfsDirectory}" ] && usage missing rootfs path
RootfsDirectory="$(readlink -m "${RootfsDirectory}")"

[ -n "${CacheDirectory}" ] && CacheDirectory="$(readlink -m "${CacheDirectory}")"

[ -d "${RootfsDirectory}" ] && usage rootfs directory: ${RootfsDirectory} directory already exists
[ -e "${RootfsDirectory}" ] && usage rootfs directory: ${RootfsDirectory} already exists as a file

[ -e "${CacheDirectory}" -a ! -d "${CacheDirectory}" ] && usage cache directory: ${CacheDirectory} must be a useable directory

# create the basic image
RBLD --init
RBLD --install task-openmoko-linux
RBLD --device-minimal

RBLD --remove exquisite
RBLD --remove exquisite-themes
RBLD --remove exquisite-theme-freerunner

# install some additional apps
RBLD --install python-lang

# finally make a tar file
RBLD --tar="${RootfsDirectory}.tar.bz2"
