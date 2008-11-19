#!/usr/bin/env python
# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# MENU: GSM module
# DESCRIPTION: test that we can use the GSM module

import time
import serial

import tests

class ATError(Exception):
    def __init__(self, msg):
        super(ATError, self).__init__(msg)

class TimeOut(ATError):
    def __init__(self):
        super(TimeOut, self).__init__("Timeout")

class Modem(object):

    def __init__(self, dev):
        self.dev = serial.Serial(dev, 115200, rtscts=1, timeout=10)

    def read_line(self):
        """read one line from the modem

        return the line striped (with /r/n removed at the end), if we
        just receive '\r\n' then this return an empty line.
        """
        ret =''
        while True:
            c = self.dev.read(1)
            if not c:
                tests.info("modem timeout")
                raise TimeOut()
            ret += c
            if ret.endswith('\r\n'):
                break
        ret = ret.strip()
        if ret:
            tests.info("recv : %s", repr(ret))
        return ret

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
        ret = []
        while True:
            line = self.read_line()
            if not line:
                continue
            if line == 'OK':
                break
            ret.append(line)
            if line.startswith('+CME ERROR'):
                raise ATError(line)
            if line.startswith('+CMS ERROR'):
                raise ATError(line)
            if line.startswith('+EXT ERROR'):
                raise ATError(line)
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

        if answer.startswith('%s:' % cmd): # standard reply
            ret = answer.split(': ', 1)[1].strip()
            return ret
        else:
            return answer

        raise ATError("Bad command format : %s" % answer)


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
        msg = self.read_line()
        tests.info("got ready messages : %s", repr(msg))
        tests.info("send empty command to calypso")
        self.dev.write('\r')
        self.dev.read()


class GSMTest(tests.Test):
    """Test the gsm module

    This test is supposed to work on both GTA02 using TI Calypso modem
    and on GTA03 with the Siemens MC75i modem.
    """

    def chat(self, cmd, error='fail'):
        try:
            return self.modem.chat(cmd)
        except ATError, e:
            err_msg = "when sending AT%s : %s" % (cmd, e)
            if error == 'fail':
                self.fail(err_msg)
            elif error == 'info':
                self.info(err_msg)
            elif error == 'abort':
                raise

    def run(self):
        self.conf = tests.parse_conf('tests.cfg')

        self.modem = Calypso('/dev/ttySAC0')
        self.modem.reset()
        self.init()
        self.test_basics()
        self.test_network()
        self.test_call()

    def init(self):
        """initialize the modem"""
        self.chat('')           # void command
        self.chat('E0')       # echo off
        self.chat('Z')        # reset
        self.chat('+CMEE=2')  # verbose error

    def test_basics(self):
        """Run some basic tests, not using the SIM"""
        self.chat('+CMUX?')      # Multiplexing mode
        self.chat('+CGMM')       # Model id
        self.chat('+CGMR')       # Firmware version
        self.chat('+CGMI')       # Manufacturer id
        ipr = self.chat('+IPR?') # Bit rate
        self.check(ipr == '115200', "check that baudrate == 115200")
        self.chat('ICF?')        # Character framing
        self.chat('S3?')         # Command line term
        self.chat('S4?')         # Response formating
        self.chat('S5?')         # Command line editing char
        self.chat('+ICF?')       # TE-TA char framing
        self.chat('+IFC?')       # Flow control (calypso != MC75i)
        self.chat('+CSCS?')      # Character set
        self.chat('+CFUN?')      # Phone functionalities
        # self.modem.chat('+CLAC')       # List of AT commands

    def test_network(self):
        """Try to register on the network"""
        self.chat('+CFUN=1') # Turn on antenna
        self.chat('+COPS=0') # Register on a network
        self.chat('+CREG?')  # check that we are registered

    def test_call(self):
        """Make phone calls"""
        number = self.conf.get('CALLABLE_NUMBER', None)
        if not number:
            self.info("can't find a callable number in conf file")
            self.info("skip call tests")
            return
        self.chat('D%s;' % number)
        self.operator_confirm("number %s is ringing within ~30 seconds",
                              number)
        self.chat('H')    # release the call
        self.operator_confirm("ringing stopped within ~10 seconds")

if __name__ == '__main__':
    GSMTest().execute()
