#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dbCollections.users import *
from dbCollections.tokens import *
from ..sendmail import *

from random import choice
import hashlib
import string

pw_length = 8


def returnModule(status, data, msg=''):
    if status == 1:
        result = {'results': 'ok', 'data': data, 'msg': msg}
    elif status == 0:
        result = {'results': 'error', 'data': data, 'msg': msg}
    return result

def createToken(data, uid):
    token = tokens()
    data['uid'] = uid
    return token.add(data)
        
def doAccountRegister(data):
    user = users()
    if (len(list(user.find(username=data['username']))) == 0) & (len(list(user.find(info__email=data['info']['email']))) == 0): 
        uid = user.add(data)
        token = createToken(data, uid)
        sendVerifyMail(data['info']['email'], data['username'], token)
        return returnModule(1, {'token': token, 'uid': uid})
    else:
        return returnModule(0, {'code': '04'}, 'An account with same email or username already registered!')

def doAccountLogin(data):
    user = users()
    if '@' in data['username']:
        result = user.find(info__email=data['username'], password=data['password'], active=True)
    else:
        result = user.find(username=data['username'], password=data['password'])
    if len(list(result)) != 0:
        u = list(result)[0]
        token = createToken(data ,u['uid'])
        return returnModule(1, {'token': token, 'uid': u['uid']})
    else:
        return returnModule(0, {'code': '02'}, 'Incorrect UserName/Password or unverified email!')

def doAccountForgotPasswd(data):
    user = users()
    result = user.find(info__email=data['email'], active=True)
    if len(list(result)) != 0:
        u = list(result)[0]
        newpassword = ''.join([choice(string.ascii_letters+string.digits) for i in range(pw_length)])
        m = hashlib.md5()
        m.update(newpassword)
        result.update_one(set__password=newpassword)
        token = createToken({'appid': '03'}, u['uid'])
        sendForgotPasswdMail(data['email'], newpassword, token)
        return returnModule(1, {'token': token, 'uid': u['uid'], 'password': newpassword})
    else:
        return returnModule(0, {'code': '04'}, 'Invalid or unverified email!')