#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *

class connector(object):
    def __init__(self, db='smartServer-refactor'):
        connect(db, host='192.168.5.60', port=27017)
