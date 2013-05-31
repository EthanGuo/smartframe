#!/usr/bin/env python  
#coding: utf-8

'''
Module define the ability need to be inject to test case. 
@version: 1.0
@author: borqsat
@see: null
'''

import os
from os.path import join
import recognization
from expectresult import ExpectResult

class Ability:
    '''
    Class to provide the assertion.
    '''
    def expect(self,name=None,interval=None,timeout=None,similarity=0.7,msg=None):
        '''
        Allows to search for a expected image in an image file that you provide (e.g. a screenshot taken and saved in a file before)
        Check whether the expected image was found that satisfy the minimum similarity requirement. If found return self,
        if not found will throw exception then test case failed 
        @type name: string
        @param name: The expected image(png) file name.
        @type interval: int
        @param interval: The interval time after one check. Default value is 3 seconds.
        @type timeout: int
        @param timeout: The duration time of waitting the screen snapshot. Default value is 9 seconds. See "runner/stability/sysconfig"
        @type similarity:float
        @param similarity: The minimum similarity a match should have. If omitted, the default is used
        @type msg:string
        @param msg: Output string if the expected image not found in the target image file. 
        @rtype: unittest.TestCase
        @return: a instance of unittest.TestCase which have the ability to interact with device and verify the checkpoint
        '''
        result = getattr(self, 'result')
        src = os.path.join(result.localpath['ws_testcase'], name)
        self.device.takeSnapshot(src)
        expect_result = ExpectResult(result.localpath['ws_testcase_right'])
        sub = expect_result.getCurrentCheckPointPath(name)
        assert recognization.isRegionMatch(src,sub)
        return self

    def exists(self,name=None,interval=None,timeout=None,similarity=0.7):
        '''
        Check whether the expected image was found that satisfy the minimum similarity requirement. If found return True, 
        If not found return False.
        @type name: string
        @param name: The expected image(png) file name.
        @type interval: int
        @param interval: The interval time after one check. Default value is 2 seconds.
        @type timeout: int
        @param timeout: The time of waitting the screen snapshot.default value is 4 seconds. See "runner/stability/sysconfig"
        @type similarity:float
        @param similarity: The minimum similarity a match should have. If omitted, the default is used
        @rtype: boolean
        @return: return ture if the expect check point exists in screen. false if not exists.
        '''
        isExists = recognization.isRegionMatch(name,origin)
        return isExists

    def find(self,text):
        '''
        check text on screen.
        '''
        pass