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


pygame.display.init()
pygame.font.init()


testDir = '/etc/test.d'
backupFile = re.compile('^(.*~|.*\.(old|orig|bak))$', re.IGNORECASE)


width, height = 480, 640
s = Screen('Test shell', width, height)

dirFrame = Frame("dir", rect = (0, 0, width, height), parent = s, background = Colour.yellow)

fontsize = 20
tOffset = 10
tWidth = width - 2 * tOffset
tHeight = 8 * fontsize
tVertical = height - tHeight - 10
status = Text('', fontsize = fontsize, rect = (tOffset, tVertical, tWidth, tHeight), parent = s)


def request(prompt):
    dialog = Dialog(prompt + "\n\n", 50, 100, s)
    dialog.run()
    return dialog.state


programList = []
buttonList = []

offset = 10
(buttonX, buttonY, buttonW, buttonH) = (offset, offset, 140, 50)
across = buttonW + offset
down = buttonH + offset

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
                               parent = dirFrame, callback = runProgram, callbackarg = p)
                buttonList.append(b)
                buttonX += across
                if buttonX + buttonW > width:
                    buttonX = offset
                    buttonY += down

eventHandler([dirFrame, status])
