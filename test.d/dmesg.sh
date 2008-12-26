#!/bin/sh
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: messages
# BEFORE: final
# AFTER: shell_functions interactive
# SECTION: info interactive
# MENU: DMESG
# DESCRIPTION: Show kernel information
# AUTHOR: Christopher Hall <hsw@openmoko.com>

# get standard test functions
. /etc/test.d/test-functions

dmesg
