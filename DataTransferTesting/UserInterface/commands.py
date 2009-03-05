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
    """run a command using the shell"""
    #print 'running:', command
    proc = subprocess.Popen(['sh', '-c', command], stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    (output, error) = proc.communicate(input)
    #print 'O:', output
    #print 'E:', error
    output = output.strip('\r\n \t')
    error = error.strip('\r\n \t')
    
    return (output, error, proc.returncode)


def remote(ip, command):
    """Run a command on a remote device ove ssh link"""
    ssh_command = 'ssh root@' + ip + ' ' + command
    #print 'run:', ssh_command
    proc = pexpect.spawn(ssh_command)

    while True:
        rc = proc.expect([r'(?i)password:', r'\(yes/no\)\?', pexpect.TIMEOUT])
        #print 'D:', proc.before
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
    (output, error, rc) = local('ifconfig ' + ether + """ | awk r'
                      /inet[[:space:]]+addr:/{
                         x = $2
                         gsub("addr:", "", x)
                         print x
                      }'
    """)
    if rc == 0 and output != '':
        return (True, output)
    return (False, 'Interface is not set up')


def ping(hostname):
    """ ping a host or IP address and return status"""
    (output, error, rc) = local('ping -c 2 -i 0.4 -w 2 ' + hostname)
    if rc == 0:
        return (True, output)
    return (False, error)


def sendOneFile(hostname, privateKey, fromFile, toFile, callback):
    """Send a local file to remote using scp"""
    command = 'scp -p -o "Compression no" -i ' + privateKey + ' ' + fromFile + ' root@' + hostname + ':' + toFile
    #(output, error, rc) = local(command)
    #if output == '':
    #    output = 'OK'
    #if rc == 0:
    #    return (True, output, command)
    #return (False, error, command)
    rc = runWithCallback(command, callback)
    return (rc == 0, str(rc), command)

def receiveOneFile(hostname, privateKey, fromFile, toFile, callback):
    """Retrieve a remote file using scp"""
    command = 'scp -p  -i ' + privateKey + ' root@' + hostname + ':' + fromFile + ' ' + toFile
    #(output, error, rc) = local(command)
    #if output == '':
    #    output = 'OK'
    #if rc == 0:
    #    return (True, output, command)
    #return (False, error, command)
    rc = runWithCallback(command, callback)
    return (rc == 0, str(rc), command)


def sendAuth(hostname, publicKey):
    """Copy public key to remote ssh configuration"""
    command = 'scp ' + publicKey + ' root@' + hostname + ':.ssh/authorized_keys'
    #print 'run:', command
    proc = pexpect.spawn(command)

    while True:
        rc = proc.expect([r'(?i)password:', r'\(yes/no\)\?', pexpect.TIMEOUT])
        #print 'D:', proc.before
        if rc == 0:
            proc.sendline('')
            proc.expect(pexpect.EOF)
            proc.close()
            #print 'X:', proc.exitstatus, '\nY:', proc.before
            return (True, 'Authentication files transferred')
        elif rc == 1:
            proc.sendline('yes')
        else:
            break
    proc.close()
    return (False, 'Send public key failed')


def runWithCallback(command, callback):
    """Run a local program calling back with every line of output"""
    #print 'run:', command
    proc = pexpect.spawn(command)

    while True:
        rc = proc.expect(['([^\n\r]*)[\r\n]', pexpect.EOF, pexpect.TIMEOUT])
        #print 'D:', proc.before
        if rc == 0:
            if not callback(proc.match.group(1)):
                #print "*TERMINATE*"
                proc.terminate()
                time.sleep(2)
                proc.kill(9)
                #proc.wait() # cannot wait if already dead
                break
        elif rc == 1:
            break
        else:
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

    print 'RWC:'
    i = 0
    def pl(s):
        global i
        i += 1
        print i, ':', s
    runWithCallback('ls -l', pl)
    print '\n-----\n'
