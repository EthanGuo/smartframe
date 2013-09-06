#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *

class Connector(object):
    def __init__(self, db='smartServer-refactor'):

        print 'init connection to db!!!'

        connect(db, host='192.168.5.60', port=27017)

connector = Connector()