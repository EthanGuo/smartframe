#!/usr/bin/env python
# -*- coding: utf-8 -*-

def resultWrapper(status, data, msg=''):
    """
    Unify the format of the return.
    """
    if status == 'ok':
        return {'result': 'ok', 'data': data, 'msg': msg}
    elif status == 'error':
        return {'result': 'error', 'data': data, 'msg': msg}