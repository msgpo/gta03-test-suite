#!/usr/bin/env python
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Main graphic shell

import sys
from stat import *
import os
from framework import *
from process import *
import pygame
from pygame.locals import *


pygame.display.init()
pygame.font.init()


testDir = '/etc/test.d'


size = width, height = 480, 640
theScreen = pygame.display.set_mode((width, height))
theScreen.fill(Colour.pink)

pygame.display.set_caption('Test Shell')

dirFrame = Frame("dir", rect = (0, 0, width, height), background = Colour.yellow)

tOffset = 10
tWidth = width - 2 * tOffset
tHeight = 8 * defaultTextSize
tVertical = height - tHeight - 10
status = Text('', fontsize = 20, rect = (tOffset, tVertical, tWidth, tHeight))

dialog = Dialog("Please answer", 50, 100)

def request(prompt):
    dialog.set(prompt + "\n")
    eventHandler(theScreen, [status, dialog])
    return dialog.state


programList = []
buttonList = []

offset = 10
(buttonX, buttonY, buttonW, buttonH) = (offset, offset, 140, 50)
across = buttonW + offset
down = buttonH + offset

def runProgram(p):
    p.run()
    return False

for f in os.listdir(testDir):

    name = os.path.join(testDir, f)
    m = os.stat(name)[ST_MODE]
    if S_ISREG(m) and (m & S_IEXEC) != 0:
        p = Process(name, request, status.append)
        if p != None:
            programList.append(p)
            b = Button(p.menu, rect = (buttonX, buttonY, buttonW, buttonH), \
                           parent = dirFrame, callback = runProgram, callbackarg = p)
            buttonList.append(b)
            buttonX += across
            if buttonX + buttonW > width:
                buttonX = offset
                buttonY += down

eventHandler(theScreen, [dirFrame, status])
