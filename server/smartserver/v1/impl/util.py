#!/usr/bin/env python
# -*- coding: utf-8 -*-
import memcache
from ..config import MEMCACHED_URI, TIME_FORMAT
from datetime import datetime

def resultWrapper(status, data, msg=''):
    """
    Unify the format of the return.
    """
    if status == 'ok':
        return {'result': 'ok', 'data': data, 'msg': msg}
    elif status == 'error':
        return {'result': 'error', 'data': data, 'msg': msg}

def convertTime(targettime):
    if targettime:
        return datetime.strptime(targettime, TIME_FORMAT).strftime(TIME_FORMAT)
    else:
        return datetime.now().strftime(TIME_FORMAT)

class Cache(object):
    def __init__(self):
        self._mc = memcache.Client(MEMCACHED_URI.split(','))

    def setCache(self, key, value=None):
        '''
        set Cache value.
        '''
        if not self._mc is None:
            self._mc.set(key, value)
        else:
            return None

    def getCache(self, key):
        '''
        get Cache value.
        '''
        if not self._mc is None:
            value = self._mc.get(key)
            return value
        else:
            return None

    def clearCache(self, key):
        '''
        get Cache value.
        '''
        if not self._mc is None:
            self._mc.delete(key)
        else:
            return None
        
cache = Cache()