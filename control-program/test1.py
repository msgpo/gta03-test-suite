# test 1
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Sample test
# AUTHOR: Christopher Hall <hsw@openmoko.com>

import Keithley
from time import sleep

#@$%^&*()sudtsffdsbm

psu = None

def setUp():
    """Set up power supply and turn on

       Also put a message on the PSU LCD to warn operator"""
    global psu
    #goop
    #assert False, "STOP ME"
    #raise Exception('kdfksdhfks')
    if debug:
        print 'setUp: **initialising**'
    psu = Keithley.PSU2303()
    psu.setCurrent(0.35)
    psu.setVoltage(3.876)
    psu.powerOn()
    if debug:
        psu.settings()
        psu.measure()
    psu.message('Test in progress  Do NOT Touch  ')

def tearDown():
    """Shutdown the power supply"""
    global psu, debug
    psu.setCurrent(0)
    psu.setVoltage(0)
    psu.powerOff()
    psu.messageOff()
    if debug:
        print 'tearDown: **cleanup**'
    del psu
    psu = None

def testZzz():
    """Run this last"""
    pass

def test001_leakage():
    """Make sure power is off and no leakage"""
    global psu
    i = psu.current
    assert abs(i) < 0.001, "Leakage current too high"

def test002_on():
    """Turn on power and wait for current to rise"""
    global psu
    for i in range(20):
        if psu.current > 0.01:
            break
        if debug:
            psu.measure()
        sleep(0.1)
    sleep(0.5)
    assert psu.current > 0.01, "Failed to Power On"

def test003_check_booted():
    """How to find out if booted?"""
    global psu
    for i in range(1000):
        if debug:
            psu.measure()
        sleep(0.1)
        i = psu.current
        assert abs(i) > 0.01, "Device failed - lost power?"
