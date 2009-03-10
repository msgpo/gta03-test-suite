#!/usr/bin/env python
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 2 or later
# NAME: touchscreen
# BEFORE: final
# AFTER: shell_functions interactive
# SECTION: touchscreen interactive
# MENU: TS
# DESCRIPTION: Simple dropout test for touchscreen
# AUTHOR: Christopher Hall <hsw@openmoko.com>

import sys
from stat import *
import os
import re

from SimpleFramework.framework import *
from SimpleFramework.colour import Colour

import pygame
from pygame.locals import *


class Theme:
    width, height = 480, 640

    class Top:
        background = Colour.yellow
        foreground = Colour.red

    class Corner:
        background = Colour.PaleGreen
        width, height = 50, 50
        foreground = Colour.red

    class Message:
        width, height = 80, 60

pygame.display.init()
pygame.font.init()


s = Screen('Touch Screen', Theme.width, Theme.height)


x = (Theme.width - Theme.Message.width) / 2
y = (Theme.height - Theme.Message.height) / 2

failed = Button("FAIL", rect = (x, y, Theme.Message.width, Theme.Message.height),
              parent = s, foreground = Colour.white, background = Colour.red)
passed = Button("PASS", rect = (x, y, Theme.Message.width, Theme.Message.height),
              parent = s, foreground = Colour.white, background = Colour.red)

def failure(arg):
    print "FAIL: Touchscreen dropout occured"
    EventHandler([failed], True).run()
    return EventHandler.EXIT_HANDLER

def success(arg):
    print "PASS: touched all corners without any dropouts"
    EventHandler([passed], True).run()
    return EventHandler.EXIT_HANDLER

last = 0
def check(arg):
    global c1, c2, c3, c4, top, last
    if c1.isBlank() and c2.isBlank() and c3.isBlank() and c4.isBlank() and top.isBlank():
        last = arg
        return EventHandler.DONE
    if c1.isBlank() or c2.isBlank() or c3.isBlank() or c4.isBlank() or top.isBlank() or last != arg:
        return failure(arg)
    return success(arg)

top = Draw('top', rect = (0, 0, Theme.width, Theme.height),
           parent = s, background = Theme.Top.background,
           foreground = Theme.Corner.foreground,
           callback = failure, callbackarg = 'error'
           )

c1 = Draw("corner1", rect = (0, 0, Theme.Corner.width, Theme.Corner.height),
          parent = top, background = Theme.Corner.background,
          foreground = Theme.Corner.foreground,
          callback = check, callbackarg = '1'
          )

c2 = Draw("corner2", rect = (0, Theme.height - Theme.Corner.height,
                             Theme.Corner.width, Theme.Corner.height),
          parent = top, background = Theme.Corner.background,
          foreground = Theme.Corner.foreground,
          callback = check, callbackarg = '2'
          )

c3 = Draw("corner3", rect = (Theme.width - Theme.Corner.width, 0,
                             Theme.Corner.width, Theme.Corner.height),
          parent = top, background = Theme.Corner.background,
          foreground = Theme.Corner.foreground,
          callback = check, callbackarg = '3'
          )

c4 = Draw("corner4", rect = (Theme.width - Theme.Corner.width, Theme.height - Theme.Corner.height,
                             Theme.Corner.width, Theme.Corner.height),
          parent = top, background = Theme.Corner.background,
          foreground = Theme.Corner.foreground,
          callback = check, callbackarg = '4'
          )


# setup and display the first screen
e = EventHandler([top])
e.run()
