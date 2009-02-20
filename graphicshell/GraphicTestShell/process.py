#!/usr/bin/env python
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 2 or later
# DESCRIPTION: Run a script on a pty
# AUTHOR: Christopher Hall <hsw@openmoko.com>

import sys
import os
import re
import select

class Process:

    MENU_RE = re.compile(r'^\s*#\s*MENU\s*:\s*(\S+(\s+\S+)*)\s*$', re.IGNORECASE)
    NONE_RE = re.compile(r'^\s*none\s*$', re.IGNORECASE)
    PROMPT_TIME = 100
    BUFFER_SIZE = 65536

    def __init__(self, fileName, requestor, callback):
        self.name = fileName
        self.menu = os.path.basename(fileName)
        self.requestor = requestor
        self.callback = callback
        self.cmd = [self.name, "-auto"]
        self.runnable = False
        f = open(fileName, "r")
        for line in f:
            m = Process.MENU_RE.match(line)
            if m:
                menuName = m.group(1)
                if not Process.NONE_RE.match(menuName):
                  self.menu = menuName
                  self.runnable = True
                  break
        f.close()


    def __repr__(self):
        return "Process " + self.menu + "('" + self.name + "')"

    def run(self):
        (pid, fd) = os.forkpty()

        # child process
        if pid == 0:
            try:
                #print 'exec:', self.cmd
                os.execvp(self.cmd[0], self.cmd)
            except OSError, e:
                print 'execution failed:', e
                print 'command was:', cmd
                sys.exit(os.EX_OSERR)

        # parent process
        selector = select.poll()

        selector.register(fd, select.POLLIN)


        run = True
        currentLine = ''
        while run:
            eventList = selector.poll(Process.PROMPT_TIME)
            if eventList == []:
                if currentLine != '':
                    if self.requestor == None:
                        os.write(fd, "no\n");
                    elif self.requestor(currentLine):
                        os.write(fd, "yes\n");
                    else:
                        os.write(fd, "no\n");
            else:
                # print eventList
                for (fd, e) in eventList:
                # print 'fd =', fd, 'e =', e
                    if (e & select.POLLIN) != 0:
                        s = os.read(fd, Process.BUFFER_SIZE)
                        s = ''.join([currentLine, s])
                        (sLeft, sSep, sRight) = s.rpartition('\n')
                        data = ''.join([sLeft, sSep])
                        if data != '':
                            self.callback(data)
                        currentLine = sRight
                    if (e & (select.POLLOUT | select.POLLERR)) == select.POLLOUT:
                        os.write(fd, "no\n");
                    if (e & select.POLLHUP) != 0:
                        run = False
                        break
        os.close(fd)
        (thePID, rc) = os.waitpid(pid, 0)
        return rc == 0


# main program
if __name__ == '__main__':
    result = ''
    def cap(s):
        global result
        result = ''.join([result, s])

    YES = re.compile(r'^\s*Y(ES)?\s*$', re.IGNORECASE)
    NO  = re.compile(r'^\s*N(O)?\s*$', re.IGNORECASE)
    # get yes/no return True/False
    def askYN(prompt):
        global YES, NO
        while True:
            s = raw_input(prompt + ' ')
            if YES.match(s):
                return True
            if NO.match(s):
                return False
            print "Unrecognised response:", s


    for f in sys.argv[1:]:
        print "Run:",f
        p = Process(f, askYN, cap)
        print "item:", p.menu
        flag = p.run()
        print "rc =", flag
        if flag:
            print '**TEST PASS**'
        else:
            print '**TEST FAIL**'

        print "***END***"
        print result

