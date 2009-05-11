# Agilent
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Classes for Serial Relay Board
# AUTHOR: Christopher Hall <hsw@openmoko.com>

from serial.serialposix import *
from time import sleep


class RelayBoard():

    def __init__(self, port = '/dev/ttyUSB1', bps = 19200):

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
        self.relay.write('{%04x}' % (self.map & 0xffff))

    def state(self):
        return self.map

    def set(self, n):
        if 1 > n or 16 < n:
            return
        self.map |= 1 << (n - 1)

    def clear(self, n):
        if 1 > n or 16 < n:
            return
        self.map &= ~(1 << (n - 1))

def main():
    r = RelayBoard()
    r.set(4)
    r.set(7)
    r.update()
    sleep(0.25)
    r.allOff()
    sleep(0.1)

    for i in range(1, 17):
      r.set(i)
      r.update()
      sleep(0.1)
      r.clear(i)

    r = None

if __name__ == '__main__':
    main()
