#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: processes
# BEFORE: final
# AFTER: shell_functions interactive
# SECTION: info interactive
# MENU: PS
# DESCRIPTION: Show kernel information
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# get standard test functions
. /etc/test.d/test-functions

ps -Aw -o pid,tty,time,cmd
