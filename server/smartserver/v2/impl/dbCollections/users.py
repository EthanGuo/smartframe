#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from connector import connector
from counter import *

import hashlib

class userinfo(EmbeddedDocument):
    phone = StringField()
    company = StringField()
    email = StringField(required=True)

class users(DynamicDocument):

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

    def add(self, appid, username, password, active, email, phone='', company=''):
        self.uid, self.password = self.__encrypte(password)
        self.appid = appid
        self.username = username
        self.active = active
        self.info = userinfo(phone=phone, company=company, email=email)
        self.save()
        return self.uid

    def findByName(self, username):
        return list(users.objects(username=username))

    def findByEmail(self, email):
        return list(users.objects(info__email=email))



