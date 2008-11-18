#!/usr/bin/env python
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# MENU: GSM module
# DESCRIPTION: test that we can use the GSM module

import time
import serial

import tests


class Modem(object):

    def __init__(self, dev):
        self.dev = serial.Serial(dev, 115200, rtscts=1, timeout=10)

    def chat(self, cmd, parser=None):
        """Send an AT command to the modem and get the reply

        Parameters:

        - cmd : the AT command we send (not including 'AT')

        - parser : the method we use to parse the reply from the
          modem. The default parser will work for most cases, but some
          specifics parsers should be used sometime.
        """
        full_cmd = 'AT%s\r' % cmd
        tests.info('send %s', repr(full_cmd))
        self.dev.write(full_cmd)
        # self.dev.flush()
        ret = ''
        while True:
            c = self.dev.read(1)
            if not c:
                break
            ret += c
            if ret.endswith('\r\nOK\r\n'):
                break
        tests.info("recv : %s", repr(ret))

        parser = parser or self.parse_answer

        return parser(cmd, ret)

    def reset(self):
        pass

    def parse_answer(self, cmd, answer):
        """Parse *most* of the AT answer messages

        This should be overriden for specific commands
        """
        if cmd.endswith('?'):   # get the stripped command
            cmd = cmd[:-1]
        elif cmd.endswith('=?'):
            cmd = cmd[:-2]

        if isinstance(answer, list):
            if len(answer) == 1:
                return self.parse_answer(cmd, answer[0])
            else:
                return [self.parse_answer(cmd, l) for l in answer]

        if '\r\n' in answer:    # Split the answer into a list
            ret = answer.split('\r\n')
            ret = [line for line in ret if line] # remove blank lines
            if ret[-1] == 'OK':
                ret = ret[:-1]
            return self.parse_answer(cmd, ret)

        if answer.startswith('%s:' % cmd): # standard reply
            ret = answer.split(': ', 1)[1].strip()
            return ret
        else:
            return answer

        raise IOError("Bad command format : %s" % answer)


class Calypso(Modem):

    def reset(self):
        """Initialize the modem before we can start sending AT commands
        """
        tests.info("turn modem off")
        sys_dir = '/sys/devices/platform/neo1973-pm-gsm.0'
        open('%s/power_on' % sys_dir, 'w').write('0')
        time.sleep(1)
        tests.info("turn modem on")
        open('%s/power_on' % sys_dir, 'w').write('1')
        time.sleep(1)
        tests.info("reset modem")
        open('%s/reset' % sys_dir, 'w').write('1')
        time.sleep(1)
        open('%s/reset' % sys_dir, 'w').write('0')
        time.sleep(4)
        msg = self.dev.read(256)
        tests.info("got ready messages : %s", repr(msg))


class GSMTest(tests.Test):
    """Test the gsm module

    This test is supposed to work on both GTA02 using TI Calypso modem
    and on GTA03 with the Siemens MC75i modem.
    """

    def run(self):
        self.modem = Calypso('/dev/ttySAC0')
        self.modem.reset()
        self.init()
        self.basics()

    def init(self):
        """initialize the modem"""
        self.modem.chat('')           # void command
        self.modem.chat('E0')       # echo off
        self.modem.chat('Z')        # reset
        self.modem.chat('+CMEE=2')  # verbose error

    def basics(self):
        """Run some basic tests, not using the SIM"""
        self.modem.chat('+CMUX?')      # Multiplexing mode
        self.modem.chat('+CGMM')       # Model id
        self.modem.chat('+CGMR')       # Firmware version
        self.modem.chat('+CGMI')       # Manufacturer id
        ipr = self.modem.chat('+IPR?') # Bit rate
        self.check(ipr == '115200', "check that baudrate == 115200")
        self.modem.chat('ICF?')        # Character framing
        self.modem.chat('S3?')         # Command line term
        self.modem.chat('S4?')         # Response formating
        self.modem.chat('S5?')         # Command line editing char
        self.modem.chat('+ICF?')       # TE-TA char framing
        self.modem.chat('+IFC?')       # Flow control (calypso != MC75i)
        self.modem.chat('+CSCS?')      # Character set
        self.modem.chat('+CFUN?')      # Phone functionalities
        # self.modem.chat('+CLAC')       # List of AT commands


if __name__ == '__main__':
    GSMTest().execute()
