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


class Theme:

    class Event:
        background = Colour.pink

    class Screen:
        background = Colour.pink

    class Frame:
        background = Colour.grey150
        foreground = Colour.black

    class Text:
        background = Colour.white
        foreground = Colour.blue
        size = 24
        font = None

    class Button:
        background = Colour.blue
        foreground = Colour.green

        class Text:
            size = 36

    class Dialog:
        border = Colour.black
        background = Colour.LightSkyBlue

        class Text:
            background = Colour.white
            foreground = Colour.blue
            size = 36
            font = None

        class Yes:
            foreground = Colour.green
            background = Colour.blue

        class No:
            foreground = Colour.red
            background = Colour.orange


class Screen(object):

    def __init__(self, name, width, height):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(name)
        self.draw()

    def draw(self):
        self.fill(Theme.Screen.background)

    def fill(self, colour):
        self.screen.fill(colour)

    def blit(self, surface, rectangle):
        self.screen.blit(surface, rectangle)

    def flip(self):
        pygame.display.flip()


class Frame(object):

    def __init__(self, name, **kwargs):

        if 'rect' in kwargs:
            (left, top, width, height) = kwargs['rect']
        else:
            raise TypeError('rect must be a 4 element tuple: (left, top, width, height)')

        self.name = name

        self.surface = pygame.Surface((width, height));
        self.rectangle = self.surface.get_rect();
        self.parent = None
        self.screen = None

        if 'parent' in kwargs:
            p = kwargs['parent']
            if isinstance(p, Screen):
                self.screen = p
            elif isinstance(p, Frame):
                self.parent = p
                self.screen = self.parent.getScreen()
            else:
                raise TypeError('parent must be a frame or screen instance')
        else:
            raise TypeError('orphaned frame')

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
            self.background = Theme.Frame.background

        if 'foreground' in kwargs:
            self.foreground = kwargs['foreground']
        else:
            self.foreground = Theme.Frame.foreground

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

    def draw(self):
        self.screen.blit(self.surface, self.rectangle)
        for c in self.children:
            c.draw()

    def drawScreen(self):
        self.screen.draw()

    def flip(self):
        self.screen.flip()

    def getScreen(self):
        return self.screen


class Text(Frame):

    def __init__(self, text, **kwargs):

        if 'background' not in kwargs:
            kwargs['background'] = Theme.Text.background
        if 'foreground' not in kwargs:
            kwargs['foreground'] = Theme.Text.foreground

        Frame.__init__(self, text, **kwargs)

        if 'fontsize' in kwargs:
            self.fontHeight = kwargs['fontsize']
        else:
            self.fontHeight = Theme.Text.size
        self.xOffset = 5
        self.fontWidth = self.rectangle.width - 2 * self.xOffset
        self.font = pygame.font.Font(Theme.Text.font, self.fontHeight)
        self.lineSize = self.font.get_linesize()
        self.text = text
        self.display()

    def display(self):
        textLines = wrap.wrap(self.text, self.font, self.fontWidth)
        self.surface.fill(self.background)
        y = self.rectangle.height
        count = 0
        for l in reversed(textLines):
            count += 1
            y -= self.lineSize
            if "FAIL" != l[0:4]:
                renderedLine = self.font.render(l, 1, self.foreground, self.background)
            else:
                renderedLine = self.font.render(l, 1, self.background, self.foreground)
            oneline = pygame.Rect(self.xOffset, y, self.fontWidth, self.fontHeight)
            self.surface.blit(renderedLine, oneline)
            if y < self.lineSize:
                break

    def append(self, text):
        self.text = ''.join([self.text, text])
        self.display()
        # special: the next lines update the display
        self.draw()
        self.flip()

    def clear(self):
        self.text = ""
        self.display()


class Button(Frame):
    def __init__(self, text, **kwargs):
        if 'background' not in kwargs:
            kwargs['background'] = Theme.Button.background
        if 'foreground' not in kwargs:
            kwargs['foreground'] = Theme.Button.foreground

        Frame.__init__(self, text, **kwargs)

        self.active = False
        self.font = pygame.font.Font(None, Theme.Button.Text.size)
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

    def __init__(self, message, x, y, parent):
        self.x = x
        self.y = y
        self.width = 400
        self.height = 300
        self.state = False

        bHeight = 80
        bWidth = 120

        tWidth = self.width - 20
        tHeight = 4 * Theme.Dialog.Text.size

        self.border = 3

        xt = (self.width - tWidth) / 2
        yt = (self.height - bHeight - tHeight) / 3
        xb = (self.width - 2 * bWidth) / 3
        yb = self.height - yt - bHeight

        Frame.__init__(self, "dialog", rect = (self.x, self.y, self.width, self.height), \
                           parent = parent, \
                           background = Theme.Dialog.border)
        self.internal = Frame("bk", \
                                  rect = (self.border, self.border, \
                                              self.width - 2  * self.border, self.height - 2  * self.border), \
                                  parent = self, background = Theme.Dialog.background)
        self.text = Text(message, rect = (xt, yt, tWidth, tHeight), parent = self.internal, \
                              foreground = Theme.Dialog.Text.foreground, background = Theme.Dialog.Text.background)

        self.yes = Button("YES", rect = (xb, yb, bWidth, bHeight), \
                              parent = self.internal, \
                              callback = self.setState, callbackarg = True, \
                              foreground = Theme.Dialog.Yes.foreground, background = Theme.Dialog.Yes.background)
        self.no = Button("NO", rect = (self.width - xb - bWidth, yb, bWidth, bHeight), \
                             parent = self.internal, \
                             callback = self.setState, callbackarg = False, \
                             foreground = Theme.Dialog.No.foreground, background = Theme.Dialog.No.background)

    def setState(self, state):
        self.state = state
        return True

    def set(self, text):
        self.text.clear()
        self.text.append(text)


    def run(self):
        save = self.screen.screen.copy()
        self.draw()
        self.screen.flip()
        run = True
        while run:
            event = pygame.event.wait()
            #print 'ev =', event
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #print event
                for frame in self.children:
                    if frame.onClick(event.pos):
                        break
                    frame.draw()
                self.screen.flip()

            elif event.type == pygame.MOUSEBUTTONUP:
                #print event
                for frame in self.children:
                    if frame.offClick(event.pos):
                        run = False
                    frame.draw()
                self.screen.flip()
        self.screen.blit(save, save.get_rect())
        self.screen.flip()




def eventHandler(frameList):
    if frameList == None:
        return

    doneScreen = False
    for frame in frameList:
        if not doneScreen:
            frame.drawScreen()
            doneScreen = True
        frame.draw()
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
                frame.draw()
            pygame.display.flip()

        elif event.type == pygame.MOUSEBUTTONUP:
            #print event
            for frame in frameList:
                if frame.offClick(event.pos):
                    run = False
                frame.draw()
            pygame.display.flip()

    frameList[0].drawScreen()
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

    def cbd(arg):
        d.run()
        return False

    width, height = 480, 640
    s = Screen("Test for Framework", width, height)

    d = Dialog("Please answer", 50, 100, parent = s)

    d.run()

    x = Frame("x", rect = (0, 0, 320, 240), parent = s, background = Colour.grey100)
    y = Frame("y", rect = (20, 20, 200, 150), parent = x, background = Colour.yellow)

    z0 = Button("z0", rect = (10, 10, 60, 50), parent = y, callback = cbz)
    z1 = Button("z1", rect = (90, 10, 60, 50), parent = y, callback = cb1)
    z2 = Button("z2", rect = (10, 90, 60, 50), parent = y, callback = cb2, foreground = Colour.green)
    z3 = Text("text", rect = (100, 100, 75, 25), parent = y)

    aa1 = Button("EXIT", rect = (300, 50, 140, 100), parent = x, foreground = Colour.white, background = Colour.red)

    aq1 = Button("ABCDEF", rect = (40, 200, 110, 100), parent = x, callback = cbx, foreground = Colour.white, background = Colour.red)
    aq2 = Button("ABCDEF", rect = (170, 200, 110, 100), parent = x, callback = cbx, foreground = Colour.white, background = Colour.green)
    aq3 = Button("ABCDEF", rect = (300, 200, 110, 100), parent = x, callback = cbx, foreground = Colour.white, background = Colour.blue)

    bt99 = Button("dialog", rect = (100, 320, 110, 100), parent = x, callback = cbd, foreground = Colour.white, background = Colour.blue)

    tOffset = 10
    tWidth = width - 2 * tOffset
    tHeight = 8 * Theme.Text.size
    tVertical = height - tHeight - 10
    t = Text("text 1\ntext 2\ntext 3\ntext 4\n", \
                 fontsize = 20, \
                 parent = s, \
                 rect = (tOffset, tVertical, tWidth, tHeight))

    eventHandler([x, t])
