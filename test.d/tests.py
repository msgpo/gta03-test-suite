# COPYRIGHT: Openmoko Inc. 2008
# LICENSE: GPL Version 2 or later
# MENU_IGNORE: YES
# DESCRIPTION: module to simplfy test script in python

"""tests module

This module is based on Chris test-function file. It provides a
compatible kind of interface for writing tests in python instead of
bash.
"""

import os
import sys


class Test(object):
    """Base class for all python tests

    To create a new test, override this class and provide a specific
    `run` method. If the run method never calls `fail`, the test is
    considered successful.
    """

    def __init__(self, out=None):
        """Create a new test instance

        Parameters:

        - out : a file object that will receive the output.  default
          to the standard output.
        """
        self.out = out or sys.stdout
        self.fail_count = 0

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
            print >> self.out, "PASS: test successful"
        elif self.fail_count == 1:
            print >> self.out, "FAIL: one test item failed"
        else:
            print >> self.out, "FAIL: %d test items failed" % self.fail_count

        return 0 if self.fail_count == 0 else 1

    def exec(self):
        """Like main except that is actually exit the program"""
        ret = self.main()
        sys.exit(ret)

    def fail(self, msg, *args):
        """Call this method if something fails"""
        print >> self.out, "FAIL: %s" % (msg % args)
        self.fail_count+=1

    def info(self, msg, *args):
        """Call this method to pass info"""
        print >> self.out, "INFO: %s" % (msg % args)


if __name__ == '__main__':

    class MyTest(Test):
        """A simple test"""

        def run(self):
            self.info("hello %d", 10)

    MyTest().main()

    class MyTest2(Test):
        """A failing test"""

        def run(self):
            self.fail("I failed :(")
            self.fail("again")

    MyTest2().main()
