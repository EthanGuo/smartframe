#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from ..config import DB_NAME, MONGODB_URI, PORT

class userinfo(EmbeddedDocument):
    email = EmailField(max_length=50)
    phonenumber = StringField()
    company = StringField()

class CaseImage(EmbeddedDocument):
    imageid = StringField()
    imagename = StringField()
    image = FileField()

class user(Document):
    """
    db schema of collection user in mongodb
    """
    username = StringField()
    password = StringField()
    info = EmbeddedDocumentField(userinfo)
    uid = SequenceField()
    appid = StringField()
    avatar = EmbeddedDocumentField(CaseImage)

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

class Log(EmbeddedDocument):
    # Work around of the mongoengine 0.8.4 AttributeError issue 
    # when invoke class.field.save() 
    log = FileField()

class cases(Document):
    """
    db schema of collection case in mongodb
    """
    gid = IntField()
    sid = IntField()
    tid = IntField()
    casename = StringField()
    domain = StringField()
    starttime = DateTimeField()
    endtime = DateTimeField()
    traceinfo = StringField()
    result = StringField()
    log = EmbeddedDocumentField(Log)
    expectshot = EmbeddedDocumentField(CaseImage)
    snapshots = ListField(EmbeddedDocumentField(CaseImage))
    comments = EmbeddedDocumentField(commentInfo)

class connector(object):
    """
    class to setup connection to mongodb
    """
    def __init__(self, db=DB_NAME):
        print "Init connection to database..."
        connect(db, host=MONGODB_URI, port=PORT)
        
connector()