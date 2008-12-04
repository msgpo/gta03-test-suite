#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: A simple installer for test images
# AUTHOR: Christopher Hall <hsw@openmoko.com>


# An interactive script that controls the root file system builder and
# allow for building QI and the kernel.  As there are already exiting
# scripts in QI and kernel directories this script just uses them.
# The intention is to have a single script that can format the SD
# card, install QI, kernel and root file system and browse the result.

BuildDirectory=$(readlink -m tmp)
ConfigurationFile=$(readlink -m .installerrc)


# configuration
# =============

# basic settings
StageDirectory="${BuildDirectory}/rootfs"

MountPoint="${BuildDirectory}/mnt"

RootFSArchive="${BuildDirectory}/rootfs.tar.bz2"

PLATFORM=gta03
URL=http://downloads.openmoko.org/repository/testing

# set to YES to completely remove the build directory
# override by command line option --clean / --no-clean
clean="NO"

# format the SD Card if the is set to YES
# override by command line option --format / --no-format
format="NO"

# enable prompting of sudo commands
# override by command line option --prompt / --no-prompt
SudoPrompt="YES"

# keep autorisation for sudo
# override by command line option --keep / --no-keep
KeepAuthorisation="NO"

# the cache directory
CacheDirectory="${BuildDirectory}/cache"

# install by default
# override by command line option --install / --no-install
InstallToSDCard="YES"

# SD Card info
SDCardDevice="sdb"
SDCardPartition="2"

# Path to the QI directory and its associated files
QiDirectory="$(readlink -m ../qi)"
QiInstaller="6410-partition-sd.sh"
QiImage="image/qi-s3c6410-"

# where to obtain kernel
KernelDirectory="$(readlink -m ../kernel)"
KernelImage="uImage-GTA03.bin"

# how to run the rootfs builder
RootFSBuilderDirectory="$(readlink -m rootfs-builder)"
RootFSBuilder="${RootFSBuilderDirectory}/rootfs-builder.sh"

# path for pre/post package scripts
RestrictedPath="${RootFSBuilderDirectory}/restricted:/bin:/usr/bin"

# the database for fakeroot must be the same as used by rootfs-builder.sh
FakerootDatabase="${StageDirectory}.frdb"

# type of image
ImageType="gta03"
KernelDirectory="$(readlink -m ../kernel)"
KernelImage="uImage-GTA03.bin"

# End of configuration
# ==================

# just in case we want to override any of the above
# read in the configuration file
[ -e "${ConfigurationFile}" ] && . "${ConfigurationFile}"


# functions

usage()
{
  [ -n "$1" ] && echo error: $*
  echo
  echo usage: $(basename "$0") '<options>'
  echo '  --clean      Completely remove build directory and package cache'
  echo '  --format     Erase and recreate SD Card filesystems'
  echo '  --prompt     Ask yes/no before sudo'
  echo '  --keep       Keep sudo authorisation'
  echo '  --install    Install to SD Card'
  echo '  --no-XXX     Turn off an option'
  exit 1
}


INFO()
{
  echo INFO: $*
}


ERROR()
{
  echo ERROR: $*
  return 1
}


AskYN()
{ 
  local yorn junk rc
  if [ X"${SudoPrompt}" != X"YES" ]
  then
    # alway assume yes if not prompting
    return 0
  fi
  while read -p "$* [y/n]? " yorn junk
  do
    case "${yorn}" in
      [yY]|[yY][eE][sS])
        return 0
        ;;
      [nN]|[nN][oO])
        return 1
        ;;
      *)
        echo Unrecognised response: ${yorn}
        ;;
    esac
  done
  return 1
}


SudoReset()
{
  if [ X"${KeepAuthorisation}" != X"YES" ]
  then
    sudo -K
  fi
}


# diplay a command an ask for permission to sudo it
# if already under sudo the just run the command
SUDO()
{
  if [ -z "${SUDO_UID}" -o -z "${SUDO_GID}" ]
  then
    echo SUDO: "$@"

    SudoReset
    if AskYN Are you really sure running this as root
    then
      sudo "$@"
    else
      echo The command was skipped
    fi
    SudoReset
  else
    "$@"
  fi
}


FakeRoot()
{
  local load=''
  if [ -e "${FakerootDatabase}" ]
  then
    fakeroot -s "${FakerootDatabase}" -i "${FakerootDatabase}" -- "$@"
  else
    fakeroot -s "${FakerootDatabase}" -- "$@"
  fi
}


RBLD_basic()
{
  ${RootFSBuilder} --url="${URL}" --platform="${PLATFORM}" --rootfs="${StageDirectory}" --path="${RestrictedPath}" "$@"
}


RBLD()
{
  local rc=0
  local cache
  if [ -n "${CacheDirectory}" -a -d "${CacheDirectory}" ]
  then
    RBLD_basic --cache="${CacheDirectory}" "$@"
    rc="$?"
  else
    RBLD_basic "$@"
    rc="$?"
  fi

  [ "${rc}" -ne 0 ] && usage Rooot Builder script failed
}


BuildRootFileSystem()
{
  rm -f "${FakerootDatabase}"
  [ -n "${StageDirectory}" ] && rm -rf "${StageDirectory}"

  RBLD --init
  RBLD --install task-openmoko-linux
  RBLD --device-minimal

  RBLD --remove exquisite
  RBLD --remove exquisite-themes
  RBLD --remove exquisite-theme-freerunner

  # install some additional apps
  #RBLD --install python-lang

  # add the test suite
  RBLD --install om-test-suite
}


SDCardMounted()
{
  mount | grep -q -s "/dev/${SDCardDevice}"
  return "$?"
}


UnmountSDCard()
{
  if SDCardMounted
  then
    SUDO umount  "/dev/${SDCardDevice}"* "${MountPoint}"
  fi
  return 0
}


MountSDCard()
{
  if ! SDCardMounted
  then
    SUDO mount  "/dev/${SDCardDevice}${SDCardPartition}" "${MountPoint}"
    return $?
  fi
  return 0
}


# temporary until we have a package
GetTheKernel()
{
  (
    cd "${KernelDirectory}" || ERROR cannt cd to: ${KernelDirectory}

    cp -p "${KernelImage}" "${StageDirectory}/boot/" || ERROR faile to copy the kernel

    env INSTALL_MOD_PATH="${StageDirectory}" make ARCH=arm modules_install || ERROR failed to install modules
    )
  if [ $? -ne 0 ]
  then
    ERROR Install kernel failed
  fi
}



# temporary hacks until om-gta03 established
ApplyFixes()
{
  case "${ImageType}" in
    [gG][tT][aA]02)
      ;;

    [gG][tT][aA]03)
      FixGTA03
      ;;
  esac
}


FixGTA03()
{
  (
    local suffix='.ORIG'

    FakeRoot find "${StageDirectory}" -name '*'"${suffix}" -delete

    # correct console, remove framebuffer login
    FakeRoot sed --in-place="${suffix}" '
             s@ttySAC2@ttySAC3@g;
             s@^1:@# &@;
             ' "${StageDirectory}/etc/inittab"

    # correct rootfs device
    FakeRoot sed --in-place="${suffix}" '
             \@^/dev/mtdblock4@{s@@/dev/mmcblk0p2@;s@jffs2@auto@;P;D}
             \@^/dev/mmcblk0p1@{s@@/dev/mtdblock4@;s@\([[:space:]]\)auto@\1jffs2@;P;D}
             ' "${StageDirectory}/etc/fstab"

    # fix busybox splash-write error
    FakeRoot rm -f "${StageDirectory}/bin/true"
    FakeRoot touch "${StageDirectory}/bin/true"
    FakeRoot chown 0:0 "${StageDirectory}/bin/true"
    FakeRoot chmod 755 "${StageDirectory}/bin/true"

    exit "$?"
    )
  if [ $? -ne 0 ]
  then
    ERROR FixGTA03 failed
  fi
}


InstallQi()
{
  local action local qi card list
  action="$1"; shift

  case "${action}" in
    [nN][oO]*)
      action=no-format
      ;;
    *)
      action=''
      ;;
  esac

  list='sdhc sd'

  UnmountSDCard || exit 1

  qi=$(ls -1 "${QiDirectory}/${QiImage}"* | head -n 1)

  INFO qi = ${qi}

  for card in ${list}
  do
    SUDO "${QiDirectory}/${QiInstaller}" "${SDCardDevice}" "${card}" "${qi}" "${action}"
    action=no-format
  done
}


InstallRootFileSystem()
{
  if [ -f "${RootFSArchive}" ]
  then
    (
      MountSDCard || exit 1

      SUDO tar xf "${RootFSArchive}" -C "${MountPoint}/"
      rc="$?"

      echo
      echo Boot directory:
      ls -l "${MountPoint}/boot"

      echo
      echo Console:
      grep '^S:' "${MountPoint}/etc/inittab"

      echo
      UnmountSDCard || true

      exit "$?"
    )
    if [ $? -ne 0 ]
    then
      ERROR install Root FS failed
    fi
  else
    ERROR Missing rootfs archive '(not built yes?)'
  fi
}

YesOrNo()
{
  local _tag _var
  _tag="$1"; shift
  _var="$1"; shift

  case "${_tag}" in
    -no-*|--no-*)
      eval "${_var}"=\"NO\"
      ;;
    *)
      eval "${_var}"=\"YES\"
      ;;
  esac
}


# main program
# ============

while [ $# -gt 0 ]
do
  arg="$1"; shift
  case "${arg}" in
    --clean|--no-clean)
      YesOrNo "${arg}" clean
      ;;
    --format|--no-format)
      YesOrNo "${arg}" format
      ;;
    --prompt|--no-prompt)
      YesOrNo "${arg}" SudoPrompt
      ;;
    --keep|--no-keep)
      YesOrNo "${arg}" KeepAuthorisation
      ;;
    --install|--no-install)
      YesOrNo "${arg}" InstallToSDCard
      ;;
    -h|--help)
      usage
      ;;
    --)
      break
      ;;
    -*)
      usage unrecognised option ${arg}
      ;;
    *)
      break
      ;;
  esac
done

UnmountSDCard

if [ X"${clean}" = X"YES" -a -d "${BuildDirectory}" ]
then
  rm -rf "${BuildDirectory}"
fi

mkdir -p "${BuildDirectory}" || usage failed to create ${BuildDirectory}
mkdir -p "${StageDirectory}" || usage failed to create ${StageDirectory}
mkdir -p "${CacheDirectory}" || usage failed to create ${StageDirectory}
mkdir -p "${MountPoint}" || usage failed to create ${MountPoint}


# build an image in the stage directory
BuildRootFileSystem
#GetTheKernel
#ApplyFixes

# create an archive of the stage directory
rm -f "${RootFSArchive}"
RBLD --tar="${RootFSArchive}"

# install to SD Card
if [ X"${InstallToSDCard}" = X"YES" ]
then
  if [ X"${format}" = X"YES" ]
  then
    InstallQi format
  else
    InstallQi no-format
  fi
  InstallRootFileSystem
fi

# finished
UnmountSDCard
