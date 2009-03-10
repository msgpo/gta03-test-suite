#!/usr/bin/env python
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 3 or later
# DESCRIPTION: Miscellaneus local and remote shell comand handling
# AUTHOR: Christopher Hall <hsw@openmoko.com>

import subprocess
import sys
import os
import os.path
import time
import pexpect


def local(command, input = None):
    """run a command using the shell

    Just captures all output and error
    and returns them as strings, along with the exit code
    """
    proc = subprocess.Popen(['sh', '-c', command], stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    (output, error) = proc.communicate(input)
    output = output.strip('\r\n \t')
    error = error.strip('\r\n \t')
    
    return (output, error, proc.returncode)


def remote(ip, command):
    """Run a command on a remote device over ssh link

    Just captures all output and error
    and returns them as strings, along with the exit code
    """
    ssh_command = 'ssh root@' + ip + ' ' + command

    proc = pexpect.spawn(ssh_command)

    while True:
        rc = proc.expect([r'(?i)password:', r'\(yes/no\)\?', pexpect.TIMEOUT])
        if rc == 0:
            proc.sendline('')
            proc.expect(pexpect.EOF)
            proc.close()
            return (True, 'OK')
        elif rc == 1:
            proc.sendline('yes')
        else:
            break
    return (False, 'Command failed: ' + ssh_command)


def getIP(ether):
    """Return the IP address of a network device"""
    proc = pexpect.spawn('ifconfig ' + ether)

    result = False
    ip = 'Interface is not set up'
    while True:
        rc = proc.expect(['inet\s+addr:\s*([0-9.]+)\s', pexpect.EOF, pexpect.TIMEOUT])
        if rc == 0:
            ip = proc.match.group(1)
            result = True
        elif rc == 1:
            break
        else:
            proc.terminate()
            time.sleep(2)
            proc.kill(9)
            break
    rc = proc.exitstatus
    proc.close()
    return (result, ip)


def ping(hostname):
    """ ping a host or IP address and return status"""
    (output, error, rc) = local('ping -c 2 -i 0.4 -w 2 "' + hostname + '"')
    if rc == 0:
        return (True, output)
    return (False, error)


def sendOneFile(hostname, privateKey, fromFile, toFile, callback):
    """Send a local file to remote using scp"""
    command = 'scp -p -o "Compression no" -i "' + privateKey + '" "' + fromFile + '" "root@' + hostname + ':' + toFile + '"'
    rc = runWithCallback(command, callback)
    return (rc == 0, str(rc), command)

def receiveOneFile(hostname, privateKey, fromFile, toFile, callback):
    """Retrieve a remote file using scp"""
    command = 'scp -p -o "Compression no" -i "' + privateKey + '" "root@' + hostname + ':' + fromFile + '" "' + toFile + '"'
    rc = runWithCallback(command, callback)
    return (rc == 0, str(rc), command)


def sendAuth(hostname, publicKey):
    """Copy public key to remote ssh configuration"""
    command = 'scp "' + publicKey + '" "root@' + hostname + ':.ssh/authorized_keys"'
    proc = pexpect.spawn(command)

    while True:
        rc = proc.expect([r'(?i)password:', r'\(yes/no\)\?', pexpect.TIMEOUT])
        if rc == 0:
            proc.sendline('')
            proc.expect(pexpect.EOF)
            proc.close()
            return (True, 'Authentication files transferred')
        elif rc == 1:
            proc.sendline('yes')
        else:
            break
    proc.close()
    return (False, 'Send public key failed')


def runWithCallback(command, callback = None):
    """Run a local program calling back with every line of output

    The command is run and each line of stdout is passed to the callback
    the callback returns True to get the next line of output
    or False to terminate the process (uses kill, then kill -9)
    """
    proc = pexpect.spawn(command)
    output = ''

    while True:
        rc = proc.expect(['([^\n\r]*)(\r*\n|\n*\r)', pexpect.EOF, pexpect.TIMEOUT])
        if rc == 0:
            if callback == None:
                pass
            elif not callback(proc.match.group(1)):
                proc.terminate()
                time.sleep(2)
                proc.kill(9)
                break
        elif rc == 1:
            break
        else:
            proc.terminate()
            time.sleep(2)
            proc.kill(9)
            break
    rc = proc.exitstatus
    proc.close()
    return rc


# if run from command line do a quick test
if __name__ == "__main__":

    command = 'ls -l /'
    (out, err, rc) = local(command)
    print 'command:', command
    print 'result:', rc
    print 'output:\n', out
    print '\n-----\nerror:\n', err
    print '\n-----\n'

    command = 'echo Just testing stderr >&2 ; exit 42'
    (out, err, rc) = local(command)
    print 'command:', command
    print 'result:', rc
    print 'output:\n', out
    print '\n-----\nerror:\n', err
    print '\n-----\n'

    print 'Run With Callback:'
    i = 0
    def pl(s):
        global i
        i += 1
        print 'RWC', i, ':', s
        return True
    runWithCallback('ls -l /boot', pl)
    print '\n-----\n'
    print 'eth0 =', getIP('eth0')
    print 'eth1 =', getIP('eth1')
    print '\n-----\n'
