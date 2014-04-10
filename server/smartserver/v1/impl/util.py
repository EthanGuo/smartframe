#!/usr/bin/env python
# -*- coding: utf-8 -*-
import memcache
from ..config import TIME_FORMAT
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