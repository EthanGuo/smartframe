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

class users(DynamicDocument):
    username = StringField()
    uid = StringField()
    password = StringField()
    appid = StringField()
    info = EmbeddedDocumentField(userinfo)

class user(users, userinfo):

    def __init__(self):
        self.connector = connector()
        
    def doInsert(self, doc):
        info = userinfo(phone=doc['info'].get('phone'), company=doc['info'].get('company'), email=doc['info'].get('email'))
        u = users(username=doc['username'], uid=doc['uid'], password=doc['password'], appid=doc['appid'], info=info)
        u.save()

    def findByName(self, name):
        return list(users.objects(username=name))

    def findByEmail(self, email):
        return list(users.objects(info__email=email))



