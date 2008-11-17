#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Build a minimal image for gta02
# AUTHOR: Christopher Hall <hsw@openmoko.com>


usage()
{
  [ -n "$1" ] && echo error: $*
  echo
  echo usage: $(basename "$0") '/path/to/rootfs'
  exit 1
}

[ -z "$1" ] && usage missing rootfs path
[ -d "$1" ] && usage rootfs directory: $1 directory already exists
[ -e "$1" ] && usage rootfs directory: $1 already exists as a file

ROOT_BUILDER_PROGRAM="$(readlink -m "$(dirname "$0")")/rootfs-builder.sh"
ROOT_FILE_SYSTEM="$(readlink -m "$1")"

ROOT_BUILDER="${ROOT_BUILDER_PROGRAM} --rootfs=${ROOT_FILE_SYSTEM}"

# create the basic image
${ROOT_BUILDER} --init
${ROOT_BUILDER} --install task-openmoko-linux
${ROOT_BUILDER} --device-minimal

${ROOT_BUILDER} --remove exquisite
${ROOT_BUILDER} --remove exquisite-themes
${ROOT_BUILDER} --remove exquisite-theme-freerunner

# install some additional apps
${ROOT_BUILDER} --install python-lang

# finally make a tar file
${ROOT_BUILDER} --tar="${ROOT_FILE_SYSTEM}.tar.bz2"
