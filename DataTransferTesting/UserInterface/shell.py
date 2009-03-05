#!/usr/bin/env python
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 3 or later
# DESCRIPTION: A simple UI to send/receive data via USB/Blutooth Ethernet
# AUTHOR: Christopher Hall <hsw@openmoko.com>

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import os
import os.path
import time
import re
import threading
import commands

# some configuration items
ssh_identity_type = 'dsa'
identity_file = 'neo_id_dsa'

home = os.getenv('HOME')
PUBLIC_KEY = os.path.join(home, '.ssh', identity_file + '.pub')
PRIVATE_KEY = os.path.join(home, '.ssh', identity_file)

# map host IP to Remote IP
NET_MAPPING = {
    '192.168.0.200': '192.168.0.202',
    '10.12.14.200': '10.12.14.202',
    '10.0.0.1': '10.0.0.2',
    '10.0.0.200': '10.0.0.202',
    }

MESSAGE_MAPPING = {
    'usb': 'Connect USB cable to device',
    'bnep': 'Enable Blutooth communications on device',
    }

def mapIP(host):
    try:
        ip = NET_MAPPING[host]
    except KeyError, e:
        ip = ''
    return ip


def messageForDevice(device):
    try:
        message = MESSAGE_MAPPING[device.rstrip('0123456789')]
    except KeyError, e:
        message = ''
    return message


def threaded(f):
    """Create a simple wrapper that allows a task to run in the background"""
    def wrapper(*args):
        t = threading.Thread(target = f, args = args)
        t.daemon = True
        t.start()
        return t
    return wrapper


class TestException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class StopTestException(TestException):
    pass


class UserInterface:

    def delete_event(self, widget, event, data = None):
        #print "delete event occurred"
        self.testStop = True
        if not self.testRunning:
            gtk.main_quit()
        return self.testRunning


#    def destroy(self, widget, data = None):
#        print "destroy signal occurred"
#        gtk.main_quit()


    def startCallback(self, widget, data = None):
        if not self.testRunning:
            self.testStop = False
            self.status.set_text('Running')
            if self.usbRadio.get_active():
                self.testRunning = True
                self.runTest('usb0')
            elif self.btRadio.get_active():
                self.testRunning = True
                self.runTest('bnep0')


    def stopCallback(self, widget, data = None):
        if self.testRunning:
            self.testStop = True
            self.status.set_text('.....Stopping.....')


    def debugCallback(self, widget, data = None):
        self.debug =  self.debugCheck.get_active()


    def appendText(self, text):
        gtk.gdk.threads_enter()
        self.buffer.insert(self.buffer.get_end_iter(), text)
        e = self.buffer.create_mark('*End*', self.buffer.get_end_iter())
        self.text.scroll_to_mark(e, 0.0, True, 0.0, 0.0)
        self.buffer.delete_mark(e)
        gtk.gdk.threads_leave()


    PERCENTAGE_RE = re.compile(r'\s([0-9]*%)')

    def getPercentage(self, text):
        m = self.PERCENTAGE_RE.search(text)
        if m:
            self.appendText('..' + m.group(1))
        else:
            self.appendText('.')
        if self.testStop:
            self.appendText(' *terminated*\n')
            return False
        return True


    def checkStop(self):
        if self.testStop:
            raise StopTestException('stop requested')


    @threaded
    def runTest(self, interface):
        """data transfer test"""

        self.appendText('\n*** Start of Test ***\n\n')
        self.appendText(messageForDevice(interface))
        self.appendText('\nProbe Interface: %s\n.' % interface)

        try:
            probe = False

            for probe_count in range(600):
                time.sleep(0.1)
                self.checkStop()

                (rc, host_ip) = commands.getIP(interface)
                if rc:
                    self.appendText('\nHost interface IP Address = ' + host_ip + '\n')

                    remote_ip = mapIP(host_ip)
                    if remote_ip == '':
                        raise TestException('Remote IP Address not found')

                    self.checkStop()

                    self.appendText('Remote IP Address = ' + remote_ip + '\n')
                    for ping_count in range(5):
                        (rc, out) = commands.ping(remote_ip)
                        if rc:
                            break
                    self.appendText(out + '\n')
                    if not rc:
                        raise TestException('Remote IP Address is not responding')

                    self.checkStop()

                    self.appendText('\nUpload ssh authentication files\n')
                    (rc, out) = commands.remote(remote_ip, 'mkdir -m 0700 -p .ssh')
                    if not rc:
                        self.appendText(out + '\n')
                        raise TestException('Unable to create ssh configuration directory')

                    self.checkStop()

                    (rc, out) = commands.sendAuth(remote_ip, PUBLIC_KEY)
                    self.appendText(out + '\n')
                    if not rc:
                        raise TestException('Unable to send Public Key file')
                        break
                    self.checkStop()

                    self.appendText('\n')
                    (output, error, rc) = commands.local('ifconfig ' + interface)
                    if rc == 0:
                        self.appendText(output + '\n')
                    else:
                        self.appendText(error + '\n')
                        raise TestException('Unable to read IP information')

                    self.appendText('\n')
                    probe = True
                    block_count = 0
                    while self.testRunning:
                        block_count += 1

                        self.appendText('%04d Send data.' % block_count)

                        (rc, out, cmd) = commands.sendOneFile(remote_ip, PRIVATE_KEY, self.send, '/tmp/usb.data',
                                                              self.getPercentage)

                        if self.debug:
                            self.appendText(cmd + ' -> ')                        
                            self.appendText(out)
                        self.appendText('\n')

                        self.checkStop()

                        self.appendText('%04d Receive data.' % block_count)

                        (rc, out, cmd) = commands.receiveOneFile(remote_ip, PRIVATE_KEY, '/tmp/usb.data', self.receive,
                                                              self.getPercentage)
                        if self.debug:
                            self.appendText(cmd + ' -> ')                        
                            self.appendText(out)
                        self.appendText('\n')

                        self.checkStop()
                    break
                elif probe_count != 0:
                    if probe_count % 50 == 0:
                        self.appendText('\n')
                    self.appendText('.')

            self.appendText('\n')
            if probe:
                raise TestException('Connection to remote failed')
        except StopTestException, e:
            if probe:
                (output, error, rc) = commands.local('ifconfig ' + interface)
                if rc == 0:
                    self.appendText(output + '\n')
                else:
                    self.appendText(error + '\n')
        except TestException, e:
            self.appendText('\n*** Test terminated ***\n')
            self.appendText('FAIL: ' + str(e) + '\n')
        except Exception, e:
            self.appendText('\n*** Test aborted ***\n')
            self.appendText('FAIL: Python Exception: ' + str(e) + '\n')
        finally:
            self.appendText('\n*** End of Test ***\n')
            self.testStop = False
            self.testRunning = False
            self.status.set_text('Stopped')


    def clearCallback(self, widget, data = None):
        """Clear screen"""
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        self.buffer.delete(start, end)


    def __init__(self, send, receive):
        """initialise application

           send    = the absolute path at this end of a block of data
           receive = the absolute path at this to store returned data
        """
        self.send = send
        self.receive = receive
        self.testRunning = False
        self.testStop = False
        self.debug = False

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_geometry_hints(None, 700, 600)

        self.window.connect("delete_event", self.delete_event)
        #self.window.connect("destroy", self.destroy)
    
        self.window.set_title('USB/Bluetooth Data Transfer Tests')
        self.window.set_border_width(10)

        vbox = gtk.VBox(False, 4)
        self.window.add(vbox)

        s = gtk.ScrolledWindow()
        s.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.text = gtk.TextView()
        self.text.set_editable(False)
        self.text.set_cursor_visible(False)
        self.buffer = self.text.get_buffer()
        s.add(self.text)
        self.text.show()
        s.show()

        vbox.pack_start(s, True, True, 10)

        radio = gtk.HBox(False, 0)

        self.usbRadio = gtk.RadioButton(None, "USB")
        radio.pack_start(self.usbRadio, False, False, 10)
        self.usbRadio.show()

        self.btRadio = gtk.RadioButton(self.usbRadio, "Bluetooth")
        radio.pack_start(self.btRadio, False, False, 10)
        self.btRadio.show()

        self.debugCheck = gtk.CheckButton('Debug')
        self.debugCheck.connect("clicked", self.debugCallback, None)
        radio.pack_end(self.debugCheck, False, False, 10)
        self.debugCheck.show()

        self.status = gtk.Label("Stopped")
        self.status.show()
        radio.pack_end(self.status, False, False, 10)

        vbox.pack_start(radio, False, False, 10)
        radio.show()

        buttons = gtk.HBox(False, 0)

        self.startTest = gtk.Button("Start Testing")
        self.startTest.connect("clicked", self.startCallback, None)
        buttons.pack_start(self.startTest, False, False, 10)
        self.startTest.show()

        self.btButton = gtk.Button("Stop Testing")
        self.btButton.connect("clicked", self.stopCallback, None)
        buttons.pack_start(self.btButton, False, False, 10)
        self.btButton.show()
    
        self.clearButton = gtk.Button("Clear Messages")
        self.clearButton.connect("clicked", self.clearCallback, None)
        buttons.pack_start(self.clearButton, False, False, 10)
        self.clearButton.show()
    

        #self.exitButton = gtk.Button("Exit Program")
        ##self.exitButton.connect("clicked", self.exitCallback, None)
        #self.exitButton.connect_object("clicked", gtk.Widget.destroy, self.window)
        #buttons.pack_start(self.exitButton, False, False, 10)
        #self.exitButton.show()

        buttons.show()
        vbox.pack_end(buttons, False, False, 10)

        vbox.show()
        self.window.show()


    def main(self):
        gtk.main()


# convenience function for main program
def eraseFile(fileName):
    if os.path.isfile(fileName):
        os.remove(fileName)


# if run from command line instantiate object and run it
if __name__ == "__main__":

    sendFile = os.path.join(os.sep, 'tmp', 'send.data')
    receiveFile = os.path.join(os.sep, 'tmp', 'receive.data')
    eraseFile(sendFile)
    eraseFile(receiveFile)
    # Create a 1MB test file
    f = open(sendFile, 'w')
    for i in range(1024):
        f.write(64 * '0123456789abcdef')
    f.close()

    if not os.path.isfile(PRIVATE_KEY):
        (output, error, rc) = commands.local('ssh-keygen -t \'%s\' -N \'\' -f \'%s\'' % (ssh_identity_type, PRIVATE_KEY))
        if rc != 0:
            print 'Public/Private key failed:', rc
            print 'stdout:'
            print output, '\n-----\nstderr:'
            print error, '\n-----'
            sys.exit(1)

    app = UserInterface(sendFile, receiveFile)
    gtk.gdk.threads_init()
    app.main()

    eraseFile(sendFile)
    eraseFile(receiveFile)
