#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *

class Connector(object):
    def __init__(self, collection, db='smartServer-refactor'):

        print 'init connection to collection %s!!!' %(collection)

        connect(db, host='192.168.5.60', port=27017)
