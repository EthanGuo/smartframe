#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import uuid
import string
from random import choice
from ..sendmail import *
from util import resultWrapper
from mongoengine import OperationError
from db import user,usetoken
import json

TOKEN_EXPIRES = {'01': 30*24*3600,
                 '02': 7*24*3600,
                 '03': 24*3600,
                 '04': 24*3600
                 }

def createToken(appid, uid):
    """
    Create a token, add it to mongodb, return the token generated.
    """
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    token = m.hexdigest()
    data = {'token':token,'appid':appid,'uid':uid,'expires':TOKEN_EXPIRES[appid]}
    tokenInst = usetoken().from_json(json.dumps(data))
    try:
        tokenInst.save()
        return {'status': 'ok', 'token': token}
    except OperationError:
        return {'status': 'error', 'token': ''}

def accountValidToken(token):
    userToken = usetoken.objects(token=token)
    if len(userToken) == 0:
        return None
    else:
        return userToken.first().uid

def accountLogin(data):
    """
    params, data: {'appid':(int)appid, 'username':(string)username, 'password':(string)password}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    #Check whether data['username'] is username or email address.
    #Find user by email/password or username/password
    if '@' in data['username']:
        data = {'appid': data['appid'], 'password': data['password'], 'info':{'email': data['username']}}
        userInst = user().from_json(json.dumps(data))
        result = user.objects(info__email = userInst.info.email,password = userInst.password)
    else:
        userInst = user().from_json(json.dumps(data))
        result = user.objects(username = userInst.username,password = userInst.password)
    #If user exists, create a token for it and return, or return error.
    if len(result) != 0:
        useraccount = result.first()
        ret = createToken(appid = useraccount.appid, uid = useraccount.uid)
        if ret['status'] == 'ok':
            rmsg, rdata, rstatus = '', {'token': ret['token'], 'uid': useraccount.uid}, 'ok'
        else:
            rmsg, rdata, rstatus = 'Create token failed!', {'code': '04'}, 'error'
    else:
        rmsg, rdata, rstatus = 'Incorrect UserName/Password!', {'code': '02'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountRegister(data):
    """
    params, data: {'username':(string)username, 'password':(string)password, 'appid':(string)appid,'info':{'email':(string), 'telephone':(string)telephone, 'company':(string)company}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    userInst = user().from_json(json.dumps(data))
    # If both username and email have not been registered, create a new user, generate a token, send a mail then return, or return error.
    if (len(user.objects(username = userInst.username)) == 0) & (len(user.objects(info__email = userInst.info.email)) == 0):
        #Password should be encryped already.
        try:
            userInst.save()
        except OperationError:
            rmsg, rdata, rstatus = 'Save user failed!', {}, 'error'
            return resultWrapper(rmsg, rdata, rstatus)
        ret = createToken(appid = userInst.appid, uid = userInst.uid)
        if ret['status'] == 'ok':
            rmsg, rdata, rstatus = '', {'token': ret['token'], 'uid': userInst.uid}, 'ok'
            #sendVerifyMail(userInst.info.email, userInst.username, ret)
        else:
            rmsg, rdata, rstatus = 'Create token failed!', {'code': '04'}, 'error'
    else:
        rmsg, rdata, rstatus = 'An account with same email or username already registered!', {'code': '04'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountForgotPasswd(data):
    """
    params, data: {'email':(string)mailaddress}
    return, data: {}
    """    
    # Find user by email, if user exists, update its password, generate a token, then send mail to it, or return error.
    result = user.objects(info__email = data['email'])
    if len(result) == 1:
        newpassword = ''.join([choice(string.ascii_letters + string.digits) for i in range(8)])
        m = hashlib.md5()
        m.update(newpassword)
        m.hexdigest()
        useraccount = result.first()
        try:
            user.objects(uid = useraccount.uid).update_one(set__password = m.hexdigest())
            useraccount.reload()
        except OperationError:
            rmsg, rdata, rstatus = 'Save new password failed!', {'code': '04'}, 'error'
        #Generate a token, then send mail to it.
        ret = createToken(appid = '03', uid = useraccount.uid)
        if ret['status'] == 'ok':
            #sendForgotPasswdMail(data['email'], newpassword, ret)
            rmsg, rdata, rstatus = '', {}, 'ok' 
        else:
            rmsg, rdata, rstatus = 'Create token failed!', {'code': '04'}, 'error'
    else:
        rmsg, rdata, rstatus = 'Invalid email!', {'code': '04'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountChangepasswd(data, uid):
    """
    params, data: {'oldpassword':(string)oldpassword, 'newpassword':(string)newpassword}
    return, data: {}
    """  
    #oldpassword/newpassword should be encrypted already.
    #Find user by user uid and oldpassword
    result = user.objects(uid = uid, password = data['oldpassword'])
    #If user exist, update its password, or return error
    if len(result) == 1:
        try:
            user.objects(uid = uid).update_one(set__password = data['newpassword'])
            list(result)[0].reload()
            rmsg, rdata, rstatus = '', {}, 'ok'
        except OperationError:
            rmsg, rdata, rstatus = 'Save new password failed!', {'code': '03'}, 'error'
    else:
        rmsg, rdata, rstatus = 'Incorrect original password!', {'code': '03'}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountInvite(data, uid):
    """
    params, data: {'email':(string)email, 'appid':(string)appid, 'username':(string)username, 'gid':(string)groupid}
    return, data: {}
    """ 
    #Send a mail to the invited user, or return error.
    #sendInviteMail(data['email'], data['username'])
    rmsg, rdata, rstatus = '', {}, 'ok'
    return resultWrapper(rmsg, rdata, rstatus)

def accountLogout(data, uid):
    """
    params, data: {'token':(string)token}
    return, data: {}
    """ 
    #Remove the token then return
    try:
        usetoken.objects(uid = uid).delete()
        rmsg, rdata, rstatus = '', {}, 'ok'
    except OperationError:
        rmsg, rdata, rstatus = 'Remove token failed!', {}, 'error'
    return resultWrapper(rmsg, rdata, rstatus)

def accountUpdate(data, uid):
    pass

def accountGetInfo(uid):
    """
    params, uid:(int)uid
    return, data: {'uid':(int)uid, 'username':(string)username, 'info': (dict)userinfo}
    """ 
    #If uid exists, return its username and info, or return error.
    result = user.objects(uid=uid)
    if len(result) == 0:
        rmsg, rdata, rstatus = 'Invalid User ID!!', {'code': '04'}, 'error'
    else:
        useraccount = result.first()
        rdata = {'uid': uid, 'username': useraccount['username'], 'info': useraccount['info']}
        rmsg, rstatus = '', 'ok'
    return resultWrapper(rmsg, rdata, rstatus)

def accountGetList(uid):
    """
    params, uid:(int)uid
    return, data: {'count':(int)count, 'users':[{'uid':(int)uid, 'username':(string)username}...]}
    """ 
    #If users exist in database, return all of them or return error
    if len(user.objects()) == 0:
        rmsg, rdata, rstatus = 'no user found!', {'code': '04'}, 'error'
    else:
        rmsg, rstatus = '', 'ok'
        users = [{'uid': d['uid'], 'username': d['username']} for d in list(user.objects())]
        rdata = {'count': len(users), 'users': users}
    return resultWrapper(rmsg, rdata, rstatus)

