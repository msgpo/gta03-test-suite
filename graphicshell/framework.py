#!/usr/bin/env python
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Simple frame and dialog box framework

import sys
import pygame
from pygame.locals import *
import wrap

pygame.display.init()
pygame.font.init()


class Colour:

    blue = (0, 0, 255)
    green = (0, 255, 0)
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    orange = (255, 165, 0)
    black = (0, 0, 0)
    grey100 = (100, 100, 100)
    grey150 = (150, 150, 150)
    white = (255, 255, 255)
    pink = (255, 200, 200)
    LightSkyBlue = (135, 206, 250)


class Scheme:

    class Event:
        background = Colour.pink

    class Frame:
        background = Colour.grey150
        foreground = Colour.black

    class Text:
        background = Colour.white
        foreground = Colour.blue

    class Button:
        background = Colour.blue
        foreground = Colour.green

    class Dialog:
        border = Colour.black
        background = Colour.LightSkyBlue

        class Text:
            background = Colour.white
            foreground = Colour.blue

        class Yes:
            foreground = Colour.green
            background = Colour.blue

        class No:
            foreground = Colour.red
            background = Colour.orange




defaultTextSize = 24
bigTextSize = 36

class Frame(object):

    def __init__(self, name, **kwargs):

        if 'rect' in kwargs:
            (left, top, width, height) = kwargs['rect']
        else:
            raise TypeError('rect must be a 4 element tuple: (left, top, width, height)')

        self.name = name

        self.surface = pygame.Surface((width, height));
        self.rectangle = self.surface.get_rect();

        if 'parent' in kwargs:
            self.parent = kwargs['parent']
        else:
            self.parent = None

        if self.parent != None:
            self.rectangle.left = left + self.parent.rectangle.left
            self.rectangle.top = top + self.parent.rectangle.top
            self.parent.add(self)
        else:
            self.rectangle.left = left
            self.rectangle.top = top

        self.children = []

        if 'background' in kwargs:
            self.background = kwargs['background']
        else:
            self.background = Scheme.Frame.background

        if 'foreground' in kwargs:
            self.foreground = kwargs['foreground']
        else:
            self.foreground = Scheme.Frame.foreground

        self.surface.fill(self.background)

    def add(self, child):
        self.children.append(child)

    def __repr__(self):
        return "Frame " + self.name + "(" + str(self.rectangle.left) + \
            ", " + str(self.rectangle.top) + \
            ", " + str(self.rectangle.width) + \
            ", " + str(self.rectangle.top) + ")"


    def onClick(self, pos):
        t = False
        for c in self.children:
            t = t or c.onClick(pos)
        return t

    def offClick(self, pos):
        t = False
        for c in self.children:
            t = t or c.offClick(pos)
        return t

    def draw(self, screen):
        screen.blit(self.surface, self.rectangle)
        for c in self.children:
            c.draw(screen)


class Text(Frame):

    def __init__(self, text, **kwargs):

        if 'background' not in kwargs:
            kwargs['background'] = Scheme.Text.background
        if 'foreground' not in kwargs:
            kwargs['foreground'] = Scheme.Text.foreground

        Frame.__init__(self, text, **kwargs)

        if 'fontsize' in kwargs:
            self.fontHeight = kwargs['fontsize']
        else:
            self.fontHeight = defaultTextSize
        self.xOffset = 5
        self.fontWidth = self.rectangle.width - 2 * self.xOffset
        self.font = pygame.font.Font(None, self.fontHeight)
        self.lineSize = self.font.get_linesize()
        self.text = text
        self.display()

    def display(self):
        textLines = wrap.wrap(self.text, self.font, self.fontWidth)
        self.surface.fill(self.background)
        y = self.rectangle.height
        for l in reversed(textLines):
            y -= self.lineSize
            renderedLine = self.font.render(l, 1, self.foreground, self.background)
            oneline = pygame.Rect(self.xOffset, y, self.fontWidth, self.fontHeight)
            self.surface.blit(renderedLine, oneline)
            if y < self.lineSize:
                break

    def append(self, text):
        self.text = ''.join([self.text, text])
        self.display()

    def clear(self):
        self.text = ""
        self.display()



class Button(Frame):
    def __init__(self, text, **kwargs):
        if 'background' not in kwargs:
            kwargs['background'] = Scheme.Button.background
        if 'foreground' not in kwargs:
            kwargs['foreground'] = Scheme.Button.foreground

        Frame.__init__(self, text, **kwargs)

        self.active = False
        self.font = pygame.font.Font(None, bigTextSize)
        self.text = text
        if 'callback' in kwargs:
            self.callback = kwargs['callback']
        else:
            self.callback = None
        if 'callbackarg' in kwargs:
            self.callbackarg = kwargs['callbackarg']
        else:
            self.callbackarg = None
        self.display()

    def onClick(self, pos):
        if self.rectangle.collidepoint(pos):
            self.active = True
            self.display()
        return False

    def offClick(self, pos):
        if self.active:
            self.active = False
            self.display()
            if self.callback != None:
                return self.callback(self.callbackarg)
            else:
                return True
        return False

    def display(self):
        if self.active:
            self.surface.fill(self.background)
            message = self.font.render(self.text, 1, self.foreground, self.background)
        else:
            self.surface.fill(self.foreground)
            message = self.font.render(self.text, 1, self.background, self.foreground)
        r = message.get_rect()
        r.center = (self.rectangle.centerx - self.rectangle.left, self.rectangle.centery - self.rectangle.top)
        self.surface.blit(message, r)


class Dialog(Frame):

    def __init__(self, message, x, y):
        self.width = 400
        self.height = 300
        self.state = False

        bHeight = 80
        bWidth = 120

        tWidth = self.width - 20
        tHeight = 4 * bigTextSize

        self.border = 3

        xt = (self.width - tWidth) / 2
        yt = (self.height - bHeight - tHeight) / 3
        xb = (self.width - 2 * bWidth) / 3
        yb = self.height - yt - bHeight

        Frame.__init__(self, "dialog", rect = (x, y, self.width, self.height), background = Scheme.Dialog.border)
        self.internal = Frame("bk", \
                                  rect = (self.border, self.border, \
                                              self.width - 2  * self.border, self.height - 2  * self.border), \
                                  parent = self, background = Scheme.Dialog.background)
        self.text = Text(message, rect = (xt, yt, tWidth, tHeight), parent = self.internal, \
                              foreground = Scheme.Dialog.Text.foreground, background = Scheme.Dialog.Text.background)

        self.yes = Button("YES", rect = (xb, yb, bWidth, bHeight), \
                              parent = self.internal, \
                              callback = self.setState, callbackarg = True, \
                              foreground = Scheme.Dialog.Yes.foreground, background = Scheme.Dialog.Yes.background)
        self.no = Button("NO", rect = (self.width - xb - bWidth, yb, bWidth, bHeight), \
                             parent = self.internal, \
                             callback = self.setState, callbackarg = False, \
                             foreground = Scheme.Dialog.No.foreground, background = Scheme.Dialog.No.background)

    def setState(self, state):
        self.state = state
        return True

    def set(self, text):
        self.text.clear()
        self.text.append(text)


def eventHandler(screen, frameList):

    screen.fill(Scheme.Event.background)
    for frame in frameList:
        frame.draw(screen)
    pygame.display.flip()

    run = True
    while run:
        event = pygame.event.wait()
        #print 'ev =', event
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #print event
            for frame in frameList:
                if frame.onClick(event.pos):
                    break
                frame.draw(screen)
            pygame.display.flip()

        elif event.type == pygame.MOUSEBUTTONUP:
            #print event
            for frame in frameList:
                if frame.offClick(event.pos):
                    run = False
                frame.draw(screen)
            pygame.display.flip()
    screen.fill(Scheme.Event.background)
    pygame.display.flip()



# main program

if __name__ == '__main__':

    def cb1(arg):
        t.append(" and a bit less text")
        return False

    def cb2(arg):
        t.append(" more text and more text")
        return False

    def cbz(arg):
        t.clear()
        return False

    def cbx(arg):
        print "callback - NOP"
        return False

    d = Dialog("Please answer", 50, 100)

    size = width, height = 480, 640
    theScreen = pygame.display.set_mode((width, height))
    theScreen.fill(Colour.background)

    pygame.display.set_caption('Framework test')

    x = Frame("x", rect = (0, 0, 320, 240), colour = Colour.grey100)
    y = Frame("y", rect =(20, 20, 200, 150), parent = x, colour = Colour.yellow)

    z0 = Button("z0", rect = (10, 10, 60, 50), parent = y, callback = cbz)
    z1 = Button("z1", rect = (90, 10, 60, 50), parent = y, callback = cb1)
    z2 = Button("z2", rect = (10, 90, 60, 50), parent = y, callback = cb2, foreground = Colour.green)
    z3 = Text("text", rect = (100, 100, 75, 25), parent = y)

    aa1 = Button("EXIT", rect = (300, 50, 140, 100), parent = x, foreground = Colour.white, background = Colour.red)

    aq1 = Button("ABCDEF", rect = (40, 200, 110, 100), parent = x, callback = cbx, foreground = Colour.white, background = Colour.red)
    aq2 = Button("ABCDEF", rect = (170, 200, 110, 100), parent = x, callback = cbx, foreground = Colour.white, background = Colour.green)
    aq3 = Button("ABCDEF", rect = (300, 200, 110, 100), parent = x, callback = cbx, foreground = Colour.white, background = Colour.blue)

    tOffset = 10
    tWidth = width - 2 * tOffset
    tHeight = 8 * defaultTextSize
    tVertical = height - tHeight - 10
    t = Text("text 1\ntext 2\ntext 3\ntext 4\n", \
                 fontsize = 20, \
                 rect = (tOffset, tVertical, tWidth, tHeight))

    eventHandler(theScreen, [x, t])
