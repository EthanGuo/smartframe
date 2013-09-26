#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import uuid
import string
from random import choice
from ..sendmail import *
from db import user,usetoken
import json

TOKEN_EXPIRES = {'01': 30*24*3600,
                 '02': 7*24*3600,
                 '03': 24*3600,
                 '04': 24*3600
                 }

def createToken(tokenType, uid):
    """
    Create a token, add it to mongodb, return the token generated.
    """
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    token = m.hexdigest()
    data = {'token':token,'tokenType':tokenType,'uid':uid,'expires':TOKEN_EXPIRES[tokenType]}
    tokenInst = usetoken().from_json(json.dumps(data))
    tokenInst.save()
    return token

def resultWrapper(msg, data, status):
    """
    Unify the format of the return.
    """
    if status == 'ok':
        return {'results': 'ok', 'data': data, 'msg': msg}
    elif status == 'error':
        return {'results': 'error', 'data': data, 'msg': msg}

def accountLogin(data):
    """
    params, data: {'tokenType':(int)tokenType, 'username':(string)username, 'password':(string)password}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    #Check whether data['username'] is username or email address.
    #Find user by email/password or username/password
    if '@' in data['username']:
        data = {'tokenType': data['tokenType'], 'password': data['password'], 'info':{'email': data['username']}}
        userInst = user().from_json(json.dumps(data))
        result = list(user.objects(info__email = userInst.info.email,password = userInst.password))
    else:
        userInst = user().from_json(json.dumps(data))
        result = list(user.objects(username = userInst.username,password = userInst.password))
    #If user exists, create a token for it and return, or return error.
    if len(result) != 0:
        useraccount = result[0]
        ret = createToken(tokenType = useraccount.tokenType, uid = useraccount.uid)
        rmsg, rdata, rstatus = '', {'token': ret, 'uid': useraccount.uid}, 'ok'
    else:
        rmsg, rdata, rstatus = 'Incorrect UserName/Password!', {'code': '02'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountRegister(data):
    """
    params, data: {'username':(string)username, 'password':(string)password, 'tokenType':(string)tokenType,'info':{'email':(string), 'telephone':(string)telephone, 'company':(string)company}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    userInst = user().from_json(json.dumps(data))
    # If both username and email have not been registered, create a new user, generate a token, send a mail then return, or return error.
    if (len(list(user.objects(username = userInst.username))) == 0) & (len(list(user.objects(info__email = userInst.info.email))) == 0):
        #Password should be encryped already.
        userInst.save()
        ret = createToken(tokenType = userInst.tokenType, uid = userInst.uid)
        #sendVerifyMail(userInst.info.email, userInst.username, ret)
        rmsg, rdata, rstatus = '', {'token': ret, 'uid': userInst.uid}, 'ok'
    else:
        rmsg, rdata, rstatus = 'An account with same email or username already registered!', {'code': '04'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountForgotPasswd(data):
    """
    params, data: {'email':(string)mailaddress}
    return, data: {}
    """    
    # Find user by email, if user exists, update its password, generate a token, then send mail to it, or return error.
    result = list(user.objects(info__email = data['email']))
    if len(result) == 1:
        newpassword = ''.join([choice(string.ascii_letters + string.digits) for i in range(8)])
        m = hashlib.md5()
        m.update(newpassword)
        m.hexdigest()
        useraccount = result[0]
        user.objects(uid = useraccount.uid).update_one(set__password = m.hexdigest())
        useraccount.reload()
        #Generate a token, then send mail to it.
        ret = createToken(tokenType = '03', uid = useraccount.uid)
        #sendForgotPasswdMail(data['email'], newpassword, ret)
        rmsg, rdata, rstatus = '', {}, 'ok' 
    else:
        rmsg, rdata, rstatus = 'Invalid email!', {'code': '04'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountChangepasswd(uid,data):
    """
    params, data: {'token':(string)token,'oldpassword':(string)oldpassword, 'newpassword':(string)newpassword}
    return, data: {}
    """  
    #oldpassword/newpassword should be encrypted already.
    #Find user by user uid and oldpassword
    result = list(user.objects(uid = uid, password = data['oldpassword']))
    #If user exist, update its password, or return error
    if len(result) == 1:
        user.objects(uid = uid).update_one(set__password = data['newpassword'])
        result[0].reload()
        rmsg, rdata, rstatus = '', {}, 'ok'
    else:
        rmsg, rdata, rstatus = 'Incorrect original password!', {'code': '03'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountInvite(uid,data):
    """
    params, data: {'token':(string)token, 'email':(string)email, 'tokenType':(string)tokenType, 'username':(string)username, 'gid':(string)groupid}
    return, data: {}
    """ 
    #Send a mail to the invited user, or return error.
    #sendInviteMail(data['email'], data['username'])
    rmsg, rdata, rstatus = '', {}, 'ok'
    return resultWrapper(rmsg, rdata, rstatus)

def accountLogout(uid,data):
    """
    params, data: {'token':(string)token}
    return, data: {}
    """ 
    #Remove the token then return
    usetoken.objects(uid = uid).update_one(unset__token = data['token'])
    rmsg, rdata, rstatus = '', {}, 'ok'
    return resultWrapper(rmsg, rdata, rstatus)

def accountUpdate():
    pass

def accountGetInfo(uid):
    """
    params, uid:(int)uid
    return, data: {'uid':(int)uid, 'username':(string)username, 'info': (dict)userinfo}
    """ 
    #If uid exists, return its username and info, or return error.
    result = list(user.objects(uid=uid))
    if len(result) == 0:
        rmsg, rdata, rstatus = 'Invalid User ID!!', {'code': '04'}, 'error'
    else:
        useraccount = result[0]
        rdata = {'uid': uid, 'username': useraccount['username'], 'info': useraccount['info']}
        rmsg, rstatus = '', 'ok'
    return resultWrapper(rmsg, rdata, rstatus)

def accountGetList(uid):
    """
    params, uid:(int)uid
    return, data: {'count':(int)count, 'users':[{'uid':(int)uid, 'username':(string)username}...]}
    """ 
    #If users exist in database, return all of them or return error
    if len(list(user.objects())) == 0:
        rmsg, rdata, rstatus = 'no user found!', {'code': '04'}, 'error'
    else:
        rmsg, rstatus = '', 'ok'
        users = [{'uid': d['uid'], 'username': d['username']} for d in list(user.objects())]
        rdata = {'count': len(users), 'users': users}
    return resultWrapper(rmsg, rdata, rstatus)

