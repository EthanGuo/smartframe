#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from ..config import DATA_DB_NAME, FILE_DB_NAME, MONGODB_URI, MONGODB_PORT

class Files(Document):
    fileid = StringField(required=True)
    filename = StringField()
    content_type = StringField()
    filedata = FileField(db_alias=FILE_DB_NAME)

    meta = {'collection': 'Files',
            'db-alias': FILE_DB_NAME,
            'indexes': [{'fields': ['fileid'], 'unique': True}],
            'index_background': True}

class UserInfo(EmbeddedDocument):
    email = EmailField(required=True, unique=True)
    phonenumber = StringField()
    company = StringField()

class Users(Document):
    """
    db schema of collection user in mongodb
    """
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    info = EmbeddedDocumentField(UserInfo)
    uid = SequenceField()
    appid = StringField()
    avatar = DictField()
    active = BooleanField(default=False)
    adminU = BooleanField(default=False)

    meta = {'collection': 'Users',
            'indexes': [{'fields': ['uid'], 'unique': True}],
            'index_background': True}

class UserTokens(Document):
    """
    db schema of collection usetoken in mongodb
    """
    uid = IntField(required=True)
    token = StringField(required=True, unique=True)
    appid = StringField()
    expires = IntField()

    meta = {'collection': 'UserTokens'}

class GroupMembers(Document):
    """
    db schema of collection groupMember in mongodb
    """
    uid = IntField(required=True)
    role = IntField(required=True)
    gid = IntField(required=True)

    meta = {'collection': 'GroupMembers'}

class Groups(Document):
    """
    db schema of collection group in mongodb
    """
    groupname = StringField(required=True, unique=True)
    gid = SequenceField()
    info = StringField()

    meta = {'collection': 'Groups',
            'indexes': [{'fields': ['gid'], 'unique': True}],
            'index_background': True}

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
    gid = IntField(required=True)
    sid = StringField(required=True)
    uid = IntField()
    endtid = IntField()
    planname = StringField()
    starttime = DateTimeField()
    endtime = DateTimeField()
    runtime = IntField()
    casecount = DictField()
    domaincount = StringField()
    enddomaincount = StringField()
    logs = ListField(DictField())
    deviceinfo = EmbeddedDocumentField(Device)

    meta = {'collection': 'Sessions',
            'indexes': [{'fields': ['sid'], 'unique': True}],
            'index_background': True}

class Cycles(Document):
    """
    db schema of collection cycle in mongodb
    """
    gid = IntField(required=True)
    sids = ListField(StringField())
    cid = SequenceField()
    product = StringField(required=True)

    meta = {'collection': 'Cycles'}

class CommentInfo(EmbeddedDocument):
    issuetype = StringField()
    commentinfo = StringField()
    caseresult = StringField()
    endsession = IntField()

class Cases(Document):
    """
    db schema of collection case in mongodb
    """
    choices=('pass', 'fail', 'error', 'running', 'block') # block is for testkit-lit
    
    sid = StringField(required=True)
    tid = IntField(required=True)
    casename = StringField(required=True)
    starttime = DateTimeField()
    endtime = DateTimeField()
    traceinfo = StringField()
    result = StringField(choices=choices)
    log = DictField()
    expectshot = DictField()
    snapshots = ListField(DictField())
    comments = EmbeddedDocumentField(CommentInfo)

    meta = {'collection': 'Cases',
            'indexes': [{'fields': ['sid', '-tid'], 'unique': True}],
            'index_background': True}

class connector(object):
    """
    class to setup connection to mongodb
    """
    def __init__(self, datadb=DATA_DB_NAME, filedb=FILE_DB_NAME):
        print "Init connection to database..."
        connect(datadb, alias='default' ,host=MONGODB_URI, port=MONGODB_PORT)
        connect(filedb, alias=filedb ,host=MONGODB_URI, port=MONGODB_PORT)
        
connector()