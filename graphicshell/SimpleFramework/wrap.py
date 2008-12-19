#!/usr/bin/env python
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Text wrapping routine

import sys
import pygame
from pygame.locals import *

pygame.font.init()


# returns: (wrapped, remainder)
def truncate(text, font, maximumWidth):
    (w, h) = font.size(text)
    index = 1
    originalText = text
    long = False
    while w > maximumWidth:
        tokens = text.rsplit(None, 1)
        text = tokens[0]
        if len(tokens) != 2:
            if long:
                text = text[:-1]
            long = True
        (w, h) = font.size(text)
    return (text, originalText[len(text):].lstrip(None))


def wrapOne(text, font, maximumWidth):
    wrapped = []
    while text != '':
        (split, text) = truncate(text, font, maximumWidth)
        wrapped.append(split)
    return wrapped


def wrap(text, font, maximumWidth):
    wrapped = []
    for text in text.splitlines():
        wrapped.extend(wrapOne(text, font, maximumWidth))
    return wrapped


# main program

if __name__ == '__main__':
    fh = 24
    fw = 240
    font=pygame.font.Font(None, fh)
    #font = pygame.font.SysFont("Times New Roman", fh)

    lines = wrap("""The first line of text says: Now is the time for all good men to come to the aid of their country
Eggs are good for you, but not on the eiffel tower
Press and hold Power button
Then while still pressing the Power button, press and hold AUX button for 5 to 8 seconds.
A boot menu will appear. This indicates the NAND flash has booted.
Press the AUX button to select one of the options and then press the Power button to execute.
should give you that information. Another way is the more recent
You should generally follow the advice given here unless you know what you are doing and have good reason to deviate.
test aLongStringWithAllOfTheSpacesLeftOutIsDifficulToWrapInAnySensibleWay hello
aLongStringWithAllOfTheSpacesLeftOutIsDifficulToWrapInAnySensibleWay hello
say aLongStringWithAllOfTheSpacesLeftOutIsDifficulToWrapInAnySensibleWay
aLongStringWithAllOfTheSpacesLeftOutIsDifficulToWrapInAnySensibleWay
FAIL: invalid parameter: /sys/devices/platform/gta02-led.0/leds/gta02-aux:red/brightness
a quick separator
FAIL: invalid parameter: /sys/devices/platform/gta02-led.0/leds/gta02-aux:red/brightness and: /sys/devices/platform/gta02-led.0/leds/gta02-aux:red/dimness
""", font, fw)

    for l in lines:
        print l
