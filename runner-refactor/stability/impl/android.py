#!/usr/bin/env python  
#coding: utf-8

'''
Android device implemention.
@version: 1.0
@author: borqsat
@see: null
'''

from devicemanager import BaseDevice
from commands import getoutput as call
from log import logger
import socket

class Device(BaseDevice):
    def __init__(self):
        '''Andorid Device for Android platform'''
        super(Device,self).__init__()
        self._con = self.__getConnect()

    def __getConnect(self):
        call('adb shell monkey --port 12345 > /dev/null')
        call('adb forward tcp:12345 tcp:12345')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 12345))
        return s

    def available(self):
        return self._con and True or False

    def recover(self):
        call('adb kill-server')
        call('adb start-server')
        call('adb shell monkey --port 12345 > /dev/null')
        call('adb forward tcp:12345 tcp:12345')
        self._con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._con.connect(('127.0.0.1', 12345))

    def touch(self,x,y):
        cmd = '%s %s %s\n'%('tap',x,y)
        self._con.send(cmd)


    def takeSnapshot(self,path):
        call('adb shell screencap /sdcard/sc.png')
        call('adb pull /sdcard/sc.png %s' % path)