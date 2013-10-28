#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from ..config import DB_NAME, MONGODB_URI, PORT

class File(EmbeddedDocument):
    # Work around of the mongoengine 0.8.4 AttributeError issue 
    # when invoke class.field.save() 
    data = FileField()

class Files(Document):
    fileid = StringField()
    filename = StringField()
    filedata = EmbeddedDocumentField(File)

    meta = {'collection': 'Files'}

class UserInfo(EmbeddedDocument):
    email = EmailField(max_length=50)
    phonenumber = StringField()
    company = StringField()

class Users(Document):
    """
    db schema of collection user in mongodb
    """
    username = StringField()
    password = StringField()
    info = EmbeddedDocumentField(UserInfo)
    uid = SequenceField()
    appid = StringField()
    avatar = StringField()
    active = BooleanField(default=False)

    meta = {'collection': 'Users'}

class UserTokens(Document):
    """
    db schema of collection usetoken in mongodb
    """
    uid = IntField()
    token = StringField()
    appid = StringField()
    expires = IntField()

    meta = {'collection': 'UserTokens'}

class GroupMembers(Document):
    """
    db schema of collection groupMember in mongodb
    """
    uid = IntField()
    role = IntField()
    gid = IntField()

    meta = {'collection': 'GroupMembers'}

class Groups(Document):
    """
    db schema of collection group in mongodb
    """
    groupname = StringField()
    gid = SequenceField()
    info = StringField()

    meta = {'collection': 'Groups'}

class Device(EmbeddedDocument):
    deviceid = StringField()
    revision = StringField()
    product = StringField()
    width = StringField()
    height = StringField()

class Sessions(Document):
    """
    db schema of collection session in mongodb
    """
    gid = IntField()
    sid = IntField()
    uid = IntField()
    planname = StringField()
    starttime = DateTimeField()
    endtime = DateTimeField()
    runtime = IntField()
    casecount = DictField()
    domaincount = DictField()
    deviceinfo = EmbeddedDocumentField(Device)

    meta = {'collection': 'Sessions'}

class Cycles(Document):
    """
    db schema of collection cycle in mongodb
    """
    gid = IntField()
    sids = ListField(IntField())
    cid = SequenceField()

    meta = {'collection': 'Cycles'}

class CommentInfo(EmbeddedDocument):
    issuetype = StringField()
    commentinfo = StringField()
    caseresult = StringField()
    endsession = StringField()

class Cases(Document):
    """
    db schema of collection case in mongodb
    """
    sid = IntField()
    tid = IntField()
    casename = StringField()
    starttime = DateTimeField()
    endtime = DateTimeField()
    traceinfo = StringField()
    result = StringField()
    log = StringField()
    expectshot = StringField()
    snapshots = ListField(StringField())
    comments = EmbeddedDocumentField(CommentInfo)

    meta = {'collection': 'Cases'}

class connector(object):
    """
    class to setup connection to mongodb
    """
    def __init__(self, db=DB_NAME):
        print "Init connection to database..."
        connect(db, host=MONGODB_URI, port=PORT)
        
connector()