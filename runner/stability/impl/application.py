'''
SmartRunner DOCUMENT
@version: 1.0
@author: U{borqsat team<www.borqs.com>}
@see: github
'''
from builder import TestBuilder
from testrunner import TestRunner
from signal import signal, SIGINT,SIGTSTP
from resulthandler import stop

class Application(object):
    '''
    Init application context of SmartRunner.
    '''
    def __init__(self,properties):
        '''
        Init test builder, test runner.

        @type properties: Obejct of CommandOptions
        @param properties: Instance of CommandOptions for user command line.
        '''
        signal(SIGINT, stop)
        signal(SIGTSTP, stop)
        self.builder = TestBuilder.getBuilder(properties)
        self.runner = TestRunner(properties)

    def run(self):
        '''
        Run the test suites.
        '''
        self.runner.runTest(self.builder.getTestSuites())