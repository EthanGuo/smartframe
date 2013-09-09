#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from connector import connector

import hashlib
import time
import uuid
import json

TOKEN_EXPIRES = {'01': 30*24*3600,
                 '02': 7*24*3600,
                 '03': 24*3600,
                 '04': 24*3600
                 }

class tokens(Document):
    uid = StringField(required=True)
    token = StringField(required=True)
    appid = StringField(required=True)
    expires = FloatField(required=True)
    info = DictField()

    def __generate(self):
        m = hashlib.md5()
        m.update(str(uuid.uuid1()))
        return m.hexdigest()

    def add(self, data):
        data['token'] = self.__generate()
        data['expires'] = (time.time() + TOKEN_EXPIRES[data['appid']])
        self.from_json(json.dumps(data)).save()
        return data['token']
