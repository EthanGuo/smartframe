#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dbCollections.users import *
from dbCollections.tokens import *
from ..sendmail import *

def createToken(data, uid):
    token = tokens()
    data['uid'] = uid
    return token.add(data)
        
def doAccountRegister(data):
    user = users()
    if (len(user.findByName(data['username'])) == 0) & (len(user.findByEmail(data['info']['email'])) == 0): 
        uid = user.add(data)
        token = createToken(data, uid)
        sendVerifyMail(data['info']['email'], data['username'], token)
        return {'results': 'ok', 'data': {'token': token, 'uid': uid}, 'msg': ''}
    else:
        return {'results': 'error', 'data': {'code': '04'}, 'msg': 'An account with same email or username already registered!'}


# def doAccountLogin(data):
#     if '@' in data['username']:
#         spec = {'info.email': data['username'], 'password': data['password'], 'active': True}
#     else:
#         spec = {'username': data['username'], 'password': data['password']}

#     fields = {'_id': 0, 'uid': 1}
#     result = store.doFind('users', spec, fields)
    
#     if len(result) != 0:
#         token = generateToken()
#         doc = {'appid': data['appid'], 'uid': result[0]['uid'],
#                'info': {}, 'token': token, 'expires': (time.time() + TOKEN_EXPIRES[data['appid']])}
        
#         store.doInsert('tokens', doc)
#         return {'results': 'ok', 'data': {'token': token, 'uid': result[0]['uid']}, 'msg': ''}
#     else:
#         return {'results': 'error', 'data':{'code': '02'}, 'msg': 'Incorrect UserName/Password or unverified email!'}
