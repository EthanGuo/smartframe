#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from connector import *

import hashlib
import time
import uuid

TOKEN_EXPIRES = {'01': 30*24*3600,
                 '02': 7*24*3600,
                 '03': 24*3600,
                 '04': 24*3600
                 }

class tokens(DynamicDocument):
    uid = StringField(required=True)
    token = StringField(required=True)
    appid = StringField(required=True)
    expires = FloatField(required=True)
    info = DictField()

    def __generate(self):
        m = hashlib.md5()
        m.update(str(uuid.uuid1()))
        return m.hexdigest()

    def add(self, appid, uid, info={}):
        self.appid = appid
        self.uid = uid
        self.token = self.__generate()
        self.expires = (time.time() + TOKEN_EXPIRES[appid])
        self.info = info
        self.save()
        return self.token

Connector("tokens")