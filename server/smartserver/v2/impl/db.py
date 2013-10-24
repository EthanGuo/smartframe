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
    uid = SequenceField()
    appid = StringField()
    avatar = StringField()

class usetoken(Document):
    """
    db schema of collection usetoken in mongodb
    """
    uid = IntField()
    token = StringField()
    appid = StringField()
    expires = IntField()

class GroupMember(Document):
    """
    db schema of collection groupMember in mongodb
    """
    uid = IntField()
    role = IntField()
    gid = IntField()

class groups(Document):
    """
    db schema of collection group in mongodb
    """
    groupname = StringField()
    gid = SequenceField()
    info = StringField()

class CountNumber(EmbeddedDocument):
    totalnum = IntField()
    passnum = IntField()
    failnum = IntField()
    errornum = IntField()

class device(EmbeddedDocument):
    revision = StringField()
    product = StringField()
    width = StringField()
    height = StringField()

class session(Document):
    """
    db schema of collection session in mongodb
    """
    gid = IntField()
    sid = IntField()
    uid = IntField()
    planname = StringField()
    starttime = DateTimeField()
    endtime = DateTimeField()
    updatetime = DateTimeField()
    casecount = EmbeddedDocumentField(CountNumber)
    deviceid = StringField()
    deviceinfo = EmbeddedDocumentField(device)

class cycle(Document):
    """
    db schema of collection cycle in mongodb
    """
    gid = IntField()
    sids = ListField(IntField())
    cid = SequenceField()

class commentInfo(EmbeddedDocument):
    issuetype = StringField()
    commentinfo = StringField()
    caseresult = StringField()
    endsession = StringField()

class cases(Document):
    """
    db schema of collection case in mongodb
    """
    sid = IntField()
    tid = IntField()
    casename = StringField()
    domain = StringField()
    starttime = DateTimeField()
    endtime = DateTimeField()
    traceinfo = StringField()
    result = StringField()
    log = StringField()
    expectshot = StringField()
    snapshots = ListField(StringField())
    comments = EmbeddedDocumentField(commentInfo)

class connector(object):
    """
    class to setup connection to mongodb
    """
    def __init__(self, db=DB_NAME):
        print "Init connection to database..."
        connect(db, host=MONGODB_URI, port=PORT)
        
connector()