#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: regulator
# BEFORE: final interactive
# AFTER: shell_functions
# SECTION: board pmu
# MENU: PMU State
# DESCRIPTION: Verify some regulator status
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# get standard test functions
. /etc/test.d/test-functions

# path to the regulator parameters

regulator_sys=/dev/null
for d in /sys/class/regulator
do
  [ -e "${d}" ] && regulator_sys="${d}" && break
done
[ ! -d "${regulator_sys}" ] && ABORT no regulators found

# name:state:min:max
regulator_list=''

reg()
{
  local name state Vmin Vmax
  name="$1"; shift
  state="$1"; shift
  Vmin="$1"; shift
  Vmax="$1"; shift

  regulator_list="${regulator_list} ${name}:${state}:${Vmin}:${Vmax}"
}

# required state of the reculators for this test
reg auto   enabled  3300000 3300000
reg down1  enabled   900000 1200000
reg down2  enabled  1800000 1800000
reg ldo1   enabled  3300000 3300000
reg ldo2   enabled  1500000 1500000
reg ldo3   enabled  3300000 3300000
reg ldo4   enabled  3000000 3000000
reg ldo5   enabled  3000000 3000000
reg ldo6   enabled  3000000 3000000
reg hcldo  enabled  2800000 2800000
reg memldo enabled  1800000 1800000

#INFO ${regulator_list}

# look up regulator in table
# the local variable must not conflich with globals
# or the eval will not produce the desired results
find()
{
  local _FindReg _FindEnable _FindMin _FindMax _FindItem
  _FindReg="$1"; shift
  _FindEnable="$1"; shift
  _FindMin="$1"; shift
  _FindMax="$1"; shift

  for _FindItem in ${regulator_list}
  do
    if [ X"${_FindItem%%:*}" = X"${_FindReg}" ]
    then
      _FindItem="${_FindItem#*:}"
      eval "${_FindEnable}"=\"${_FindItem%%:*}\"
      _FindItem="${_FindItem#*:}"
      eval "${_FindMin}"=\"${_FindItem%%:*}\"
      _FindItem="${_FindItem#*:}"
      eval "${_FindMax}"=\"${_FindItem%%:*}\"
      return 0
    fi
  done
  return 1
}


for r in "${regulator_sys}"/*
do
 name=$(GET_VALUE "${r}/name")
 state=$(GET_VALUE "${r}/state")
 microvolts=$(GET_VALUE "${r}/microvolts")
 min_microvolts=$(GET_VALUE "${r}/min_microvolts")
 max_microvolts=$(GET_VALUE "${r}/max_microvolts")

 STATUS checking regulator ${name} '@' ${r}

 if find "${name}" enable min max
 then
   [ X"${state}" != X"${enable}" ] && FAIL ${name}: is ${state} but should be ${enable}
   [ ${min} -ne ${min_microvolts} ] && FAIL ${name}: min_microvolts=${min_microvolts} is wrong, should be ${min}
   [ ${max} -ne ${max_microvolts} ] && FAIL ${name}: max_microvolts=${max_microvolts} is wrong, should be ${max}
   [ ${microvolts} -gt ${max_microvolts} ] && FAIL ${name}: over voltage: ${microvolts} '>' ${max_microvolts}
   [ ${microvolts} -lt ${min_microvolts} ] && FAIL ${name}: under voltage: ${microvolts} '<' ${min_microvolts}
 else
   FAIL no testing parameters for regulator: ${name}
 fi

done
