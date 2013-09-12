#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dbCollections.users import *
from dbCollections.tokens import *
from ..sendmail import *

from random import choice
import hashlib
import string

def returnModule(status, data, msg=''):
    result = {'results': status, 'data': data, 'msg': msg}
    return result

def createToken(data, uid):
    token = tokens()
    data['uid'] = uid
    return token.add(data)
        
def doAccountRegister(data):
    user = users()
    if (len(user.find(username=data['username'])) == 0) & (len(user.find(info__email=data['info']['email'])) == 0): 
        uid = user.add(data)
        token = createToken(data, uid)
        sendVerifyMail(data['info']['email'], data['username'], token)
        return returnModule('ok', {'token': token, 'uid': uid})
    else:
        return returnModule('error', {'code': '04'}, 'An account with same email or username already registered!')

def doAccountLogin(data):
    user = users()
    if '@' in data['username']:
        result = user.find(info__email=data['username'], password=data['password'], active=True)
    else:
        result = user.find(username=data['username'], password=data['password'])
    if len(result) != 0:
        token = createToken(data ,result[0]['uid'])
        return returnModule('ok', {'token': token, 'uid': result[0]['uid']})
    else:
        return returnModule('error', {'code': '02'}, 'Incorrect UserName/Password or unverified email!')

def doAccountForgotPasswd(data):
    user = users()
    result = user.find(info__email=data['email'], active=True)
    if len(result) != 0:
        newpassword = ''.join([choice(string.ascii_letters+string.digits) for i in range(8)])
        m = hashlib.md5()
        m.update(newpassword)
        ###########################
        user.update(m.hexdigest())
        ###########################
        token = createToken({'appid': '03'}, result[0]['uid'])
        sendForgotPasswdMail(data['email'], newpassword, token)
        return returnModule('ok', {'token': token, 'uid': result[0]['uid'], 'password': newpassword})
    else:
        return returnModule('error', {'code': '04'}, 'Invalid or unverified email!')