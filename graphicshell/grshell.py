#!/usr/bin/env python
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Main graphic shell

import sys
from stat import *
import os
import re
from framework import *
from process import *
import pygame
from pygame.locals import *


class Theme:
    width, height = 480, 640
    gap = 10

    class Menu:
        background = Colour.yellow
        class Button:
            foreground = Colour.LightSteelBlue2
            background = Colour.blue
            perRow = 3
            perColumn = 7

    class Dialog:
        x = 50
        y = 100

    class Status:
        fontsize = 20
        lines = 10

        class Default:
            foreground = Colour.blue
            background = Colour.grey85
        class Pass:
            foreground = Colour.blue
            background = Colour.PaleGreen
        class Fail:
            foreground = Colour.red
            background = Colour.white


pygame.display.init()
pygame.font.init()


testDir = '/etc/test.d'
backupFile = re.compile('^(.*~|.*\.(old|orig|bak))$', re.IGNORECASE)


s = Screen('Test shell', Theme.width, Theme.height)

dirFrame = Frame("dir", rect = (0, 0, Theme.width, Theme.height), parent = s, background = Theme.Menu.background)

# the gaps bwtween everything

tWidth = Theme.width - 2 * Theme.gap
tHeight = Theme.Status.lines * Theme.Status.fontsize
tVertical = Theme.height - tHeight - Theme.gap
status = Text('', fontsize = Theme.Status.fontsize, \
                  rect = (Theme.gap, tVertical, tWidth, tHeight), parent = s, \
                  background = Theme.Status.Default.background, \
                  foreground = Theme.Status.Default.foreground, \
                  )

status.addTag('FAIL', Theme.Status.Fail.foreground, Theme.Status.Fail.background)
status.addTag('PASS', Theme.Status.Pass.foreground, Theme.Status.Pass.background)

def request(prompt):
    dialog = Dialog(prompt + "\n \n", Theme.Dialog.x, Theme.Dialog.y, s)
    dialog.run()
    return dialog.state


programList = []
buttonList = []

buttonW = (Theme.width - (Theme.Menu.Button.perRow + 1) * Theme.gap) / Theme.Menu.Button.perRow
buttonH = (Theme.height - (Theme.Menu.Button.perColumn + 2) * Theme.gap - tHeight) / Theme.Menu.Button.perColumn
(buttonX, buttonY) = (Theme.gap, Theme.gap)
across = buttonW + Theme.gap
down = buttonH + Theme.gap

def runProgram(p):
    status.draw()
    status.flip()
    p.run()
    return False

for f in os.listdir(testDir):
    if not backupFile.match(f):
        name = os.path.join(testDir, f)
        m = os.stat(name)[ST_MODE]
        if S_ISREG(m) and (m & S_IEXEC) != 0:
            p = Process(name, request, status.append)
            if p != None and p.runnable:
                programList.append(p)
                b = Button(p.menu, rect = (buttonX, buttonY, buttonW, buttonH), \
                               background = Theme.Menu.Button.background, \
                               foreground = Theme.Menu.Button.foreground, \
                               parent = dirFrame, callback = runProgram, callbackarg = p)
                buttonList.append(b)
                buttonX += across
                if buttonX + buttonW > Theme.width:
                    buttonX = Theme.gap
                    buttonY += down

eventHandler([dirFrame, status])
