#!/usr/bin/env python
# -*- coding: utf-8 -*-

from schema.users import *

class DataStore(object):

    def __init__(self):

        print 'init db store class!!!'

        self.users = user()

db = DataStore()
