#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *

class userinfo(EmbeddedDocument):
    email = EmailField(max_length=50)
    phonenumber = StringField()
    company = StringField()

class user(Document):
    """
    db schema of collection user in mongodb
    """
    username = StringField()
    password = StringField()
    info = EmbeddedDocumentField(userinfo)
    active = BooleanField()
    uid = SequenceField()
    appid = StringField()
    groupname = StringField()

class usetoken(Document):
    """
    db schema of collection usetoken in mongodb
    """
    uid = IntField()
    token = StringField()
    appid = StringField()
    expires = IntField()

class connector(object):
    """
    class to setup connection to mongodb
    """
    def __init__(self, db='smartServer-refactor'):
        connect(db, host='192.168.5.60', port=27017)
        
connector()