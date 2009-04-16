# TestS1
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Sample test
# AUTHOR: Christopher Hall <hsw@openmoko.com>

import Keithley
import Agilent
from time import sleep

psu = None
dmm = None

def setUp():
    """Set up power supply and turn on

       Also put a message on the PSU LCD to warn operator"""
    global psu, dmm

    if debug:
        print 'setUp: **initialising**'

    dmm = Agilent.DMM34401A(22)
    dmm.setVoltageDC()

    psu = Keithley.PSU2303(7)
    psu.setCurrent(0.25)
    psu.setVoltage(0)
    psu.powerOn()
    if debug:
        psu.settings()
        psu.measure()
    psu.message('Test in progress  Do NOT Touch  ')

def tearDown():
    """Shutdown the power supply"""
    global psu, dmm, debug
    psu.setCurrent(0)
    psu.setVoltage(0)
    psu.powerOff()
    psu.messageOff()
    if debug:
        print 'tearDown: **cleanup**'
    del psu
    del dmm
    psu = None
    dmm = None

def testZzz():
    """Run this last"""
    pass

def test001_leakage():
    """Make sure power is off and no leakage"""
    global psu, dmm
    voltage = 2.0
    for i in range(30):
        psu.setVoltage(voltage)
        voltage += 0.05
        i = psu.current
        assert abs(i) < 0.001, "Leakage current too high"
        info('V = %7.3f' % dmm.voltage)
        sleep(0.05)
    psu.setVoltage(0)

def test002_on():
    """Step voltage and read back"""
    global psu, dmm

    psu.setVoltage(3)
    info('V = %7.3f' % dmm.voltage)

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
