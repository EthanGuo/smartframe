#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *

# class group_members(EmbeddedDocument):
#     role = StringField()
#     user = ReferenceField(users)

# class groups(DynamicDocument):
#     groupname = StringField()
#     gid = StringField()
#     info = StringField()
#     groupmember = ListField(EmbeddedDocument(group_members))

# class testresults(DynamicDocument):
#     tid = StringField()
#     sid = StringField()
#     gid = StringField()
#     casename = StringField()
#     starttime = StringField()
#     endtime = StringField()
#     result = StringField()
#     log = StringField()
#     snapshots = StringField()
#     traceinfo = StringField()

# class deviceInfo(EmbeddedDocument):
#     width = StringField()
#     height = StringField()
#     product = StringField()
#     revision = StringField()

# class summary(EmbeddedDocument):
#     Total = StringField()
#     Pass = StringField()
#     Fail = StringField()
#     Error = StringField()

# class testsessions(DynamicDocument):
#     sid = StringField()
#     cid = StringField()
#     gid = StringField()
#     starttime = StringField()
#     endtime = StringField()
#     runtime = StringField()
#     tester = StringField()
#     planname = StringField()
#     deviceId = StringField()
#     deviceinfo = EmbeddedDocumentField(deviceInfo)
#     summary = EmbeddedDocumentField(summary)

class tokens(Document):
    uid = StringField()
    token = StringField()
    appid = StringField()
    expires = StringField()

class counter(DynamicDocument):
    tag = StringField()
    next = StringField()

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
    
def main():
    connect('smartServer-refactor', host='192.168.5.60', port='27017')


if __name__ == '__main__':
    main()
