#!/usr/bin/env python
# -*- coding: utf-8 -*-

def resultWrapper(msg, data, status):
    """
    Unify the format of the return.
    """
    if status == 'ok':
        return {'results': 'ok', 'data': data, 'msg': msg}
    elif status == 'error':
        return {'results': 'error', 'data': data, 'msg': msg}