# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# NAME: python_functions
# BEFORE: final
# AFTER: shell_functions
# SECTION: init norun nomenu
# MENU: none
# DESCRIPTION: module to simplfy test script in python
# AUTHOR: Guillaume Chereau <charlie@openmoko.org>

"""tests module

This module is based on Chris test-function file. It provides a
compatible kind of interface for writing tests in python instead of
bash.
"""

import os
import sys

# The output stream for all tests
out = sys.stdout


def info(msg, *args):
    """Print an INFO message to the output"""
    print >> out, "INFO: %s" % (msg % args)


def parse_conf(file):
    """parse a conf file in the bash format and return a dictionary
    key->value
    """
    ret = {}
    file = open(file)
    for line in file:
        if line.startswith('#'):
            continue
        tokens = line.split('=', 1)
        if len(tokens) == 2:
            ret[tokens[0]] = tokens[1].strip()
    return ret


class Test(object):
    """Base class for all python tests

    To create a new test, override this class and provide a specific
    `run` method. If the run method never calls `fail`, the test is
    considered successful.
    """

    def __init__(self):
        """Create a new test instance
        """
        self.fail_count = 0
        self.total_count = 0

    def run(self):
        """Override this method to write your own tests"""
        pass

    def main(self):
        """The main method of the test

        It performs the test, print the PASS or FAIL message, and then
        return the exit value (0 for success, 1 for failure).
        """
        try:
            self.run()
        except Exception, e:
            self.fail("Got exception : %s", e)

        if self.fail_count == 0:
            print >> out, "PASS: test successful"
        elif self.fail_count == 1:
            print >> out, "FAIL: one test item failed"
        else:
            print >> out, "FAIL: %d test items failed" % self.fail_count

        return 0 if self.fail_count == 0 else 1

    def execute(self):
        """Like main except that is actually exit the program"""
        ret = self.main()
        sys.exit(ret)

    def fail(self, msg, *args):
        """Call this method if something fails"""
        print >> out, "FAIL: %s" % (msg % args)
        self.fail_count += 1
        self.total_count += 1
        return False

    def check(self, cond, msg, *args):
        """Check that a condition is satisfied"""
        if not cond:
            return self.fail(msg, *args)
        else:
            return self.pass_(msg, *args)

    def info(self, msg, *args):
        """Call this method to pass info"""
        info(msg, *args)

    def operator_confirm(self, msg, *args):
        """Ask a yes/no question to the operator, fail if the answer is no"""
        while True:
            answer = raw_input("CONFIRM: %s [y/n]? " % msg % args)
            answer = answer.split()[0].lower()
            if answer in ['y', 'yes']:
                self.pass_(msg, *args)
            elif answer in ['n', 'no']:
                self.fail(msg, *args)
            else:
                print >> out, "Unrecognised response: %s" % answer
                continue
            break

    def pass_(self, msg, *args):
        """Pass a test"""
        print >> out, "PASS: %s" % (msg % args)
        self.total_count += 1
        return True


if __name__ == '__main__':

    class MyTest(Test):
        """A simple test"""

        def run(self):
            self.info("hello %d", 10)
            self.operator_confirm("are you here")

    MyTest().main()

    class MyTest2(Test):
        """A failing test"""

        def run(self):
            self.fail("I failed :(")
            self.fail("again")

    MyTest2().main()
