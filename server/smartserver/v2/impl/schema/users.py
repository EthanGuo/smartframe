#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from connector import *

# class tokens(Document):
#     uid = StringField()
#     token = StringField()
#     appid = StringField()
#     expires = StringField()

# class counter(DynamicDocument):
#     tag = StringField()
#     next = StringField()

class userinfo(EmbeddedDocument):
    phone = StringField()
    company = StringField()
    email = StringField()

class user(DynamicDocument):
    username = StringField()
    uid = StringField()
    password = StringField()
    appid = StringField()
    info = EmbeddedDocumentField(userinfo)

class modify(user):

    def __init__(self):
        self.connector = connector()
        
    def add(self, obj):
        obj.save()

    def findByName(self, name):
        return list(user.objects(username=name))

    def findByEmail(self, email):
        return list(user.objects(info__email=email))



