#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: verify the metadata for a test script
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# defaults

verbose="NO"

# XXX Still debugging
RCORDER="$(dirname "$0")/../rcorder/rcorder"

# functions

usage()
{
  [ -n "$1" ] && echo error: $*
  echo
  echo usage: $(basename "$0") '<options>'
  echo '  --skip=section    Ignore tests in the following section'
  echo '  --keep=section    Include tests in the following section'
  echo '  --verbose         Display some more info'
  exit 1
}


INFO()
{
  case "${verbose}" in
    [yY]|[yY][eE][sS])
      echo INFO: $*
      ;;
    *)
      ;;
  esac
}


NOTICE()
{
  echo NOTICE: $*
}


ERROR()
{
  echo ERROR: $*
  return 1
}


# main program
# ============

trap "echo '*terminated*'; exit 1" INT

SkipList='-s norun'
KeepList=

while [ $# -gt 0 ]
do
  arg="$1"; shift
  case "${arg}" in
    --verbose)
      verbose="YES"
      ;;
    --skip=*)
      SkipList="${SkipList} -s ${arg#*=}"
      ;;
    --keep=*)
      KeepList="${KeepList} -k ${arg#*=}"
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


# sequence the tests

INFO run ${RCORDER}
TestList="$(${RCORDER} ${KeepList} ${SkipList} /etc/test.d/*)"


# run the tests

TestCount=0
SuccessCount=0
FailCount=0

INFO starting tests
for item in ${TestList}
do
 TestCount=$((${TestCount} + 1))
 NOTICE running [${TestCount}]: ${item}
 (exec ${item} || exit 1)
 if [ $? -eq 0 ]
 then
   INFO test: ${item} succeeded
   SuccessCount=$((${SuccessCount} + 1))
 else
   ERROR test: ${item} failed
   FailCount=$((${FailCount} + 1))
 fi
done


# summarise results

echo
echo Test results: ${SuccessCount}/${TestCount}
if [ "${FailCount}" -eq 1 ]
then
  echo '             ' 1 test failed
elif [ "${FailCount}" -gt 1 ]
then
  echo '             ' ${FailCount} tests failed
fi
