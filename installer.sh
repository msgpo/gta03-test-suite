#!/bin/bash
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

ConfigurationChanged=NO

KernelStageDirectory="${BuildDirectory}/kernel"
RootFSStageDirectory="${BuildDirectory}/rootfs"
MountPoint="${BuildDirectory}/mnt"
RootFSArchive="${BuildDirectory}/rootfs.tar.bz2"


usage()
{
  [ -n "$1" ] && echo error: $*
  echo
  echo usage: $(basename "$0") '<options>'
  exit 1
}


# diplay a command an ask for permission to sudo it
# if already under sudo the just run the command
SUDO()
{
  if [ -z "${SUDO_UID}" -o -z "${SUDO_GID}" ]
  then
    echo SUDO: "$@"
    case "${config_paranoia_level}" in
      [mM][oO][rR][eE])
        sudo -K
        ;;
      [lL][eE][sS][sS])
        ;;
      *)
        ;;
    esac
    if AskYN Are you really sure running this as root
    then
      sudo "$@"
    else
      echo The command was skipped
    fi
    case "${config_paranoia_level}" in
      [mM][oO][rR][eE])
        sudo -K
        ;;
      [lL][eE][sS][sS])
        ;;
      *)
        ;;
    esac
  else
    "$@"
  fi
}


INFO()
{
  echo INFO: $*
  return 1
}


ERROR()
{
  echo ERROR: $*
  return 1
}


ConfigVariable()
{
  local variable type default description current
  variable="$1"; shift
  type="$1"; shift
  default="$1"; shift
  description="$1"; shift

  eval current=\"\${${variable}}\"

  [ -n "${current}" ] && return

  echo The variable ${variable} has not been configured yet

  read -p "${variable} = [${default}]? " current
  [ -z "${current}" ] && current="${default}"

  eval "${variable}"="\"${current}\""
 
  ConfigurationChanged=YES
}


# this routine is bash specific
AllVariables()
{
  echo ${!config_@}
}


WriteConfiguration()
{
  local variable value

  if [ X"${ConfigurationChanged}" = X"YES" ]
  then
    rm -f "${ConfigurationFile}"

    for variable in $(AllVariables)
    do
      eval value=\"\${${variable}}\"
      echo ${variable}="'"${value}"'" >> "${ConfigurationFile}"
    done
  fi
}


DisplayConfiguration()
{
  local variable value

  echo Contents of: ${ConfigurationFile}
  echo

  for variable in $(AllVariables)
  do
    eval value=\"\${${variable}}\"
    echo ${variable}="'"${value}"'"
  done

  echo
  echo Configuration that is not part of configuration file
  echo
  echo 'build directory   =' ${BuildDirectory}
  echo 'kernel staging    =' ${KernelStageDirectory}
  echo 'root fs staging   =' ${RootFSStageDirectory}
  echo 'local mount point =' ${MountPoint}
}


AskYN()
{ 
  local yorn junk rc
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


SDCardMounted()
{
  mount | grep -q -s "/dev/${config_device}"
  return "$?"
}


UnmountSDCard()
{
  if SDCardMounted
  then
    SUDO umount  "/dev/${config_device}"* "${MountPoint}"
  fi
  return 0
}


MountSDCard()
{
  if ! SDCardMounted
  then
    SUDO mount  "/dev/${config_device}${config_partition}" "${MountPoint}"
    return $?
  fi
  return 0
}


CleanQI()
{
  (
    cd "${config_qi}" || exit 1

    make clean || exit 1

    )
  if [ $? -ne 0 ]
  then
    ERROR Clean QI failed
  fi
}


BuildQI()
{
  local action local cwd qi card list
  action="$1"; shift

  case "${action}" in
    no*)
      action=no-format
      ;;
    *)
      action=''
      ;;
  esac

  list='sdhc sd'

  UnmountSDCard || exit 1

  cwd="${PWD}"

  (
    cd "${config_qi}" || exit 1

    "${config_qi}/${config_qi_build}" || exit 1

    qi=$(ls -1 "${config_qi_image}"* | head -n 1)

    INFO qi = ${qi}

    for card in ${list}
    do
      SUDO "${config_qi}/${config_qi_install}" "${config_device}" "${card}" "${qi}" "${action}"
      action=no-format
    done

    )
  if [ $? -ne 0 ]
  then
    ERROR Install QI failed
  fi
}


CleanKernel()
{
  (
    cd "${config_kernel}" || exit 1

    make clean || exit 1

    )
  if [ $? -ne 0 ]
  then
    ERROR Clean kernel failed
  fi
}


BuildKernel()
{
  (
    cd "${config_kernel}" || exit 1

    cp "${config_kernel_conf}" .config || exit 1

    "${config_kernel}/${config_kernel_build}" || exit 1

    ##env INSTALL_MOD_PATH="${KernelStageDirectory}" make ARCH=arm install || exit 1
    cp -p "${config_kernel_image}" "${KernelStageDirectory}" || exit 1

    env INSTALL_MOD_PATH="${KernelStageDirectory}" make ARCH=arm modules_install || exit 1

    )
  if [ $? -ne 0 ]
  then
    ERROR Build kerrefs/remotes/origin/andy-tracking.nel failed
  fi
}


InstallKernel()
{
  if [ -f  "${KernelStageDirectory}/${config_kernel_image}" ]
  then
    (
      MountSDCard || exit 1

      SUDO cp -p "${KernelStageDirectory}/${config_kernel_image}" "${MountPoint}/boot/${config_kernel_install_image}" || exit 1
      SUDO cp -pr "${KernelStageDirectory}/lib/modules" "${MountPoint}/lib/" || exit 1

      exit "$?"
      )
    if [ $? -ne 0 ]
    then
      ERROR Install kernel failed
    fi
  else
    ERROR No kernel image to install '(not built yes?)'
  fi
}


BuildRootFS()
{
  if [ -d "${RootFSStageDirectory}" ]
  then
    if AskYN Root FS has already been built, erase and rebuild
    then
      rm -rf "${RootFSStageDirectory}"
    else
      INFO Not building Root FS
      return 0
    fi
  fi
  (
    "${config_rootfs}/${config_rootfs_build}" "${RootFSStageDirectory}" "${config_cache}" || exit 1
    )
  if [ $? -ne 0 ]
  then
    ERROR Build Root FS failed
  fi
}


InstallRootFS()
{
  if [ -f "${RootFSArchive}" ]
  then
    (
      MountSDCard || exit 1

      SUDO tar xf "${RootFSArchive}" -C "${MountPoint}/"

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


fix()
{
  case "${config_fix_mode}" in
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
    MountSDCard || exit 1

    local suffix='.ORIG'

    SUDO find "${MountPoint}" -name '*'"${suffix}" -delete

    SUDO sed --in-place="${suffix}" '
             s@ttySAC2@ttySAC3@g;
             s@^1:@# &@;
             ' "${MountPoint}/etc/inittab"

    SUDO sed --in-place="${suffix}" '
             \@^/dev/mtdblock4@{s@@/dev/mmcblk0p2@;s@jffs2@auto@;P;D}
             \@^/dev/mmcblk0p1@{s@@/dev/mtdblock4@;s@\([[:space:]]\)auto@\1jffs2@;P;D}
             ' "${MountPoint}/etc/fstab"

    exit "$?"
    )
  if [ $? -ne 0 ]
  then
    ERROR FixGTA03 failed
  fi
}


# main program
# ============

[ -e "${ConfigurationFile}" ] && . "${ConfigurationFile}"

mkdir -p "${BuildDirectory}" || usage failed to create ${BuildDirectory}
mkdir -p "${KernelStageDirectory}" || usage failed to create ${KernelStageDirectory}
mkdir -p "${MountPoint}" || usage failed to create ${MountPoint}

ConfigVariable config_device device "sdb" "Name of the SD card device"
ConfigVariable config_partition device "2" "Number of the SD card partition [1..4]"

ConfigVariable config_qi directory "$(readlink -m ../qi)" "Path to the QI directory"
ConfigVariable config_qi_build file "build" "name of the QI build script"
ConfigVariable config_qi_install file "6410-partition-sd.sh" "Name of the QI installer script"
ConfigVariable config_qi_image file "image/qi-s3c6410-" "Prefix of QI image"
ConfigVariable config_qi_update command "git pull --rebase" "Command to update QI to latest version"

ConfigVariable config_kernel directory "$(readlink -m ../kernel)" "Path to the kernel directory"
ConfigVariable config_kernel_conf file "arch/arm/configs/gta03_defconfig" "Name of default kernel config"
ConfigVariable config_kernel_build file "build" "Name of the kernel build script"
ConfigVariable config_kernel_image file "uImage-GTA03.bin" "Name of the kernel image"
ConfigVariable config_kernel_install_image file "uImage-GTA03.bin" "Name of the installed kernel image"
ConfigVariable config_kernel_update command "git pull --rebase" "Command to update kernel to latest version"

ConfigVariable config_rootfs directory "$(readlink -m rootfs-builder)" "Path to Root FS builder"
ConfigVariable config_rootfs_build file "mini.sh" "Name of the Root FS build script"

ConfigVariable config_cache directory "$(readlink -m cache)" "Path to opkg cache directory"

ConfigVariable config_fix_mode word "gta03" "fix /etc for particular hardware"

ConfigVariable config_paranoia_level word "more" "how paranoid are you [more/less]"

WriteConfiguration

help=YES

while :
do
  echo
  [ -d "${KernelStageDirectory}" ] && INFO Kernel Stage Directory exists
  [ -d "${RootFSStageDirectory}" ] && INFO Root FS Stage Directory exists
  [ -f "${RootFSArchive}" ] && INFO Root FS Archive exists
  SDCardMounted && INFO SD Card is Mounted - remember to umount before removal
  echo
  if [ X"${help}" = X"YES" ]
  then
    echo 'help    - This message'
    echo 'format  - format SD card and install QI'
    echo 'qi      - reinstall qi'
    echo 'kernel  - configure, build and stage kernel'
    echo 'root    - build and stage root file system'
    echo 'install - install kernel and root file system'
    echo 'update  - use git to update the qi and the kernel'
    echo 'ls      - list the files on the SD Card'
    echo 'lynx    - browse the files on the SD Card'
    echo 'umount  - unmount the SD card'
    echo 'stage   - browse the files in the staging directory'
    echo 'clean   - clean kernel and QI'
    echo 'unstage - clean kernel and root fs staging directories'
    echo 'conf    - display configuration'
    echo 'exit    - end program'
    echo
    help=NO
  fi
  command=''
  while [ -z "${command}" ]
  do
    read -p 'Command: ' command junk
  done

  case "${command}" in
    ex*|x|qu*)
      break
      ;;
    he*|\?)
      help=YES
      ;;
    un*)
      [ -n "${KernelStageDirectory}" ] && SUDO rm -rf "${KernelStageDirectory}"
      [ -n "${RootFSStageDirectory}" ] && SUDO rm -rf "${RootFSStageDirectory}"
      [ -n "${RootFSArchive}" ] && SUDO rm -rf "${RootFSArchive}"
      ;;
    cl*)
      CleanQI
      CleanKernel
      ;;
    fo*)
      BuildQI format
      ;;
    qi)
      BuildQI no-format
      ;;
    ke*)
      BuildKernel
      ;;
    ro*)
      BuildRootFS
      ;;
    in*)
      AskYN Install Root FS && InstallRootFS
      AskYN Install Kernel && InstallKernel
      AskYN Apply fixes for "${config_fix_mode}" && fix
      ;;
    up*)
      ${config_qi_update}
      ${config_kernel_update}
      ;;
    co*)
      DisplayConfiguration
      ;;
    ls)
      MountSDCard
      ls -lR "${RootFSStageDirectory}" | less
      ;;
    ly*)
      MountSDCard
      lynx "${MountPoint}"
      ;;
    st*)
      lynx "${BuildDirectory}"
      ;;
    um*)
      UnmountSDCard
      ;;
    *)
      echo Invalid command: ${command}
      ;;
  esac

done

UnmountSDCard
