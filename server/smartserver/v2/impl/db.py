#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from ..config import DB_NAME, MONGODB_URI, PORT

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

class usetoken(Document):
    """
    db schema of collection usetoken in mongodb
    """
    uid = IntField()
    token = StringField()
    appid = StringField()
    expires = IntField()

class groupMember(EmbeddedDocument):
    uid = IntField()
    role = IntField()

class groups(Document):
    """
    db schema of collection group in mongodb
    """
    groupname = StringField()
    gid = SequenceField()
    members = ListField(EmbeddedDocumentField(groupMember))

class connector(object):
    """
    class to setup connection to mongodb
    """
    def __init__(self, db=DB_NAME):
        print "Init connection to database..."
        connect(db, host=MONGODB_URI, port=PORT)
        
connector()