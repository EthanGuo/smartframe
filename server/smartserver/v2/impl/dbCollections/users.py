#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from connector import connector
from counter import *

import hashlib
import json

class userinfo(EmbeddedDocument):
    phone = StringField()
    company = StringField()
    email = StringField(required=True)

class users(Document):

    username = StringField(required=True, unique=True)
    uid = StringField(required=True)
    password = StringField(required=True)
    appid = StringField(required=True)
    active = BooleanField(required=True)
    info = EmbeddedDocumentField(userinfo)

    meta = {'allow_inheritance': True}

    def __count(self, keyname):
        c = counter()
        return c.Find_and_Modify(keyname)

    def __encrypte(self, password):
        m = hashlib.md5()
        m.update(password)
        pswd = m.hexdigest()
        m.update('%08d' % self.__count('userid'))
        uid = m.hexdigest()
        return uid, pswd

    def add(self, data):
        data['uid'], data['password'] = self.__encrypte(data['password'])
        data['active'] = True if data.get('active') else False
        self.from_json(json.dumps(data)).save()
        return data['uid']

    def find(self, **kwargs):
        return list(users.objects(**kwargs))
