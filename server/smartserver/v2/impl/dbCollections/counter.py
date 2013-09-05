#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from connector import *

class counter(DynamicDocument):
    tag = StringField()
    next = IntField()

    def Find_and_Modify(self, keyname):
        next = counter.objects.get_or_create(tag=keyname, defaults={'next': 1})[0]['next']
        counter.objects(tag=keyname).update(inc__next=1)
        return next
        
Connector("counter")