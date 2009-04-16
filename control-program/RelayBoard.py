# Agilent
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Classes for Serial Relay Board
# AUTHOR: Christopher Hall <hsw@openmoko.com>

from serial.serialposix import *
from time import sleep


class RelayBoard():

    def __init__(self, port = '/dev/ttyUSB0', bps = 19200):

        self.relay = Serial(port = port, baudrate = bps)
        self.relay.open()
        self.allOff()


    def __del__(self):
        self.relay.close()


    def allOff(self):
        self.map = 0
        self.update()


    def update(self):
        print '{%04x}' % (self.map & 0xffff)


    @property
    def on(self):
        return 0


    @on.setter
    def on(self, n):
        if 1 > n or 16 < n:
            return
        map |= 1 << (n - 1)
        self.update()

def main():
    r = RelayBoard()
    r.on = 4
    r = None

if __name__ == '__main__':
    main()
