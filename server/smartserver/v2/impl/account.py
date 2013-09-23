#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import uuid
import string
from random import choice
from ..sendmail import *
from dbSchema import user,usetoken
import json

TOKEN_EXPIRES = {'01': 30*24*3600,
                 '02': 7*24*3600,
                 '03': 24*3600,
                 '04': 24*3600
                 }

def createToken(appid, uid):
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    token = m.hexdigest()
    data = {'token':token,'appid':appid,'uid':uid,'expires':TOKEN_EXPIRES[appid]}
    tokenInst = usetoken().from_json(json.dumps(data))
    tokenInst.save()
    return token

def resultWrapper(msg,data):
    if msg =='':
        return {'results': 'ok', 'data':data, 'msg': ''}
    else:
        return {'results': 'error', 'data':data, 'msg':msg}

def accountLogin(data):
    userInst = user().from_json(json.dumps(data))
    if userInst.info.email != None:
        result = list(user.objects(info__email = userInst.info.email,password = userInst.password))
    else:
        result = list(user.objects(username = userInst.username,password = userInst.password))
    if len(result) != 0:
        for useraccount in result:
            ret = createToken(appid = data['appid'], uid = useraccount.uid)
            rmsg, rdata = '', {'token': ret, 'uid': useraccount.uid}
    else:
        rmsg, rdata = 'Incorrect UserName/Password or unverified email!', {'code': '02'}
    return resultWrapper(rmsg, rdata)

def accountRegister(data):
    userInst = user().from_json(json.dumps(data))
    result = list(user.objects(username = userInst.username,info__email = userInst.info.email))
    if len(result) == 0:
        m = hashlib.md5()
        m.update(data['password'])
        userInst.password = m.hexdigest()
        userInst.save()
        ret = createToken(appid = data['appid'], uid = userInst.uid)
        sendVerifyMail(data['info']['email'], data['username'], ret)
        rmsg, rdata = '', {'token': ret, 'uid': userInst.uid}
    else:
        rmsg, rdata = 'An account with same email or username already registered!', {'code': '04'}
    return resultWrapper(rmsg, rdata)


def accountForgotPasswd(data):
    userInst = user().from_json(json.dumps(data))
    if userInst.info.email != None:
        result = list(user.objects(info__email = userInst.info.email))
        if len(result) == 1:
            newpassword = ''.join([choice(string.ascii_letters + string.digits) for i in range(8)])
            m = hashlib.md5()
            m.update(newpassword)
            m.hexdigest()
            for useraccount in result:
                res = user.objects(uid = useraccount.uid).update_one(set__password = m.hexdigest())
                useraccount.reload()
                if res == False:
                    rmsg, rdata = 'Reset passwod unsucessfully!!!', {'code': '04'}
                else:
                   ret = createToken(appid = '03', uid = useraccount.uid)
                   useraccount['token'] = ret
                   userdata = user.to_json(useraccount)
                   rmsg, rdata = '', userdata 
        else:
            rmsg, rdata = 'Invalid or unverified email!', {'code': '04'}
    else:
        rmsg, rdata = 'Invalid request, mail can not be null!', {'code': '04'}
    return resultWrapper(rmsg, rdata)

def accountChangepasswd(userid,data):
    m = hashlib.md5()
    m.update(data['oldpassword'])
    oldpassword = m.hexdigest()
    result = list(user.objects(uid = userid, password = oldpassword))
    if len(result) == 1:
        m = hashlib.md5()
        m.update(data['newpassword'])
        user.objects(uid = userid).update_one(set__password = m.hexdigest())
        rmsg, rdata = '', {'uid': userid}
    else:
        rmsg, rdata = 'Incorrect original password!', {'code': '03'}
    return resultWrapper(rmsg, rdata)


def accountInvite(userid,data):
    userInst = user().from_json(json.dumps(data))
    usertoken = createToken(appid = userInst.appid, uid = userid)
    if usertoken != None:
        sendInviteMail(userInst.info.email, userInst.username,userInst.groupname, usertoken)
        rmsg, rdata = '', {'uid': userid, 'token': usertoken}
    else:
        rmsg, rdata = 'Create token fail!', {'code': '03'}
    return resultWrapper(rmsg, rdata)

def accountLogout(userid,data):
    result = usetoken.objects(uid = userid).update_one(unset__token = data['token'])
    if result == True:
        rmsg, rdata = '', 1
    else:
        rmsg, rdata = 'delete token fail!', {'code': '03'}
    return resultWrapper(rmsg, rdata)

def accountUpdate():
    pass

def doAccountGetInfo():
    pass

def doAccountGetList(uid):
    if len(list(user.objects())) == 0:
        rmsg, rdata = 'no user found!', {'code': '04'}
    else:
        rmsg = ''
        users = [{'uid': d['uid'], 'username': d['username']} for d in list(user.objects())]
        rdata = {'count': len(users), 'users': users}
    return resultWrapper(rmsg, rdata)

