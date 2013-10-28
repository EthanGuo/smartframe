#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib, uuid
import string, json
from random import choice
from ..sendmail import *
from util import resultWrapper
from mongoengine import OperationError
from db import Users, UserTokens, Groups, Sessions, GroupMembers
from filedealer import saveFile
import time

TOKEN_EXPIRES = {'01': 30*24*3600, # For client end upload result purpose 
                 '02': 7*24*3600, #For browser user.
                 }

def createToken(appid, uid):
    """
    Create a token, add it to mongodb, return the token generated.
    """
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    token = m.hexdigest()
    data = {'token':token,'appid':appid,'uid':uid,'expires':(TOKEN_EXPIRES[appid] + time.time())}
    tokenInst = UserTokens().from_json(json.dumps(data))
    try:
        tokenInst.save()
        return {'status': 'ok', 'token': token}
    except OperationError:
        return {'status': 'error', 'token': ''}

def accountValidToken(token):
    userToken = UserTokens.objects(token=token).first()
    if userToken == 0:
        return None
    else:
        return userToken.uid

def accountLogin(data):
    """
    params, data: {'appid':(string), 'username':(string), 'password':(string)}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    #Check whether data['username'] is username or email address.
    #Find user by email/password or username/password
    if '@' in data.get('username'):
        result = Users.objects(info__email=data['username'], password=data['password'])
    else:
        result = Users.objects(username=data['username'], password=data['password'])
    #If user exists, create a token for it and return, or return error.
    if len(result) != 0:
        #TODO: check the active status of user here.
        useraccount = result.first()
        ret = createToken(appid=useraccount.appid, uid=useraccount.uid)
        if ret['status'] == 'ok':
            rmsg, rdata, rstatus = '', {'token': ret['token'], 'uid': useraccount.uid}, 'ok'
        else:
            rmsg, rdata, rstatus = 'Create token failed!', {}, 'error'
    else:
        rmsg, rdata, rstatus = 'Incorrect UserName/Password!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def accountRegister(data):
    """
    params, data: {'username':(string), 'password':(string), 'appid':(string),
                   'info':{'email':(string), 'telephone':(string), 'company':(string)}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    # If both username and email have not been registered, create a new user, generate a token, send a mail then return, or return error.
    if (len(Users.objects(username=data['username'])) == 0) & (len(Users.objects(info__email=data['info']['email'])) == 0):
        #Password should be encryped already.
        try:
            userInst = Users().from_json(json.dumps(data))
            userInst.save()
        except OperationError:
            rmsg, rdata, rstatus = 'Save user failed!', {}, 'error'
            return resultWrapper(rstatus, rdata, rmsg)
        ret = createToken(appid=userInst.appid, uid=userInst.uid)
        if ret['status'] == 'ok':
            rmsg, rdata, rstatus = '', {'token': ret['token'], 'uid': userInst.uid}, 'ok'
            #sendVerifyMail(userInst.info.email, userInst.username, ret)
        else:
            rmsg, rdata, rstatus = 'Create token failed!', {}, 'error'
    else:
        rmsg, rdata, rstatus = 'An account with same email or username already registered!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def accountRetrievePasswd(data):
    """
    params, data: {'email':(string)mailaddress}
    return, data: {}
    """    
    # Find user by email, if user exists, update its password, generate a token, then send mail to it, or return error.
    result = Users.objects(info__email=data.get('email'))
    if len(result) == 1:
        newpassword = ''.join([choice(string.ascii_letters + string.digits) for i in range(8)])
        m = hashlib.md5()
        m.update(newpassword)
        m.hexdigest()
        useraccount = result.first()
        try:
            Users.objects(uid=useraccount.uid).update_one(set__password=m.hexdigest())
            useraccount.reload()
        except OperationError:
            rmsg, rdata, rstatus = 'Save new password failed!', {}, 'error'
        #Generate a token, then send mail to it.
        ret = createToken(appid='02', uid=useraccount.uid)
        if ret['status'] == 'ok':
            #sendForgotPasswdMail(data['email'], newpassword, ret)
            rmsg, rdata, rstatus = '', {}, 'ok' 
        else:
            rmsg, rdata, rstatus = 'Create token failed!', {}, 'error'
    else:
        rmsg, rdata, rstatus = 'Invalid email!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def accountChangepasswd(data, uid):
    """
    params, data: {'oldpassword':(string)oldpassword, 'newpassword':(string)newpassword}
    return, data: {}
    """  
    #oldpassword/newpassword should be encrypted already.
    #Find user by user uid and oldpassword
    result = Users.objects(uid=uid, password=data.get('oldpassword'))
    #If user exist, update its password, or return error
    if len(result) == 1:
        try:
            Users.objects(uid=uid).update_one(set__password=data.get('newpassword'))
            list(result)[0].reload()
            rmsg, rdata, rstatus = '', {}, 'ok'
        except OperationError:
            rmsg, rdata, rstatus = 'Save new password failed!', {}, 'error'
    else:
        rmsg, rdata, rstatus = 'Incorrect original password!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def accountInvite(data, uid):
    """
    params, data: {'email':(string)email, 'username':(string)username}
    return, data: {}
    """ 
    #Send a mail to the invited user, or return error.
    #sendInviteMail(data['email'], data['username'])
    rmsg, rdata, rstatus = '', {}, 'ok'
    return resultWrapper(rstatus, rdata, rmsg)

def accountLogout(data, uid):
    """
    params, data: {}
    return, data: {}
    """ 
    #Remove the token then return
    try:
        UserTokens.objects(uid=uid).delete()
        rmsg, rdata, rstatus = '', {}, 'ok'
    except OperationError:
        rmsg, rdata, rstatus = 'Remove token failed!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def __updateAvatar(data, uid):
    """
       Update avatar here
    """
    filetype = data['file'].get('filename').split('.')[-1]
    if not filetype in ['png', 'jpg', 'jpeg']:
        return resultWrapper('error', {}, 'Support png/jpg/jpeg image only!')
    filedata = data['file'].get('file')
    u = Users.objects(uid=uid).first()
    if u.avatar:
        u.avatar.image.delete()
    imageid = saveFile(filedata, 'image/' + filetype, data['file']['filename'])
    try:
        Users.objects(uid=uid).update(set__avatar=imageid)
    except OperationError:
        return resultWrapper('error', {}, 'Update avatar failed!')
    return resultWrapper('ok', {}, 'Upload successfully!')

def accountUpdate(data, uid):
    """
    params, data: {'appid': (string)appid, 'username': (string)username, 'company': (string)company, 'telephone': (string)phone, 'file': (dict)file}
    return, data: {'token': (string)token}
    """ 
    if 'file' in data.keys():
        return __updateAvatar(data, uid)
    else:
        try:
            if data.has_key('username'):
                Users.objects(uid=uid).update(set__username=data['username'])
            if data.has_key('company'):
                Users.objects(uid=uid).update(set__info__company=data['company'])
            if data.has_key('telephone'):
                Users.objects(uid=uid).update(set__info__phonenumber=data['telephone'])
        except OperationError:
            return resultWrapper('error', {}, 'Update user info failed!')
        result = createToken(data['appid'], uid)
        if result['status'] == 'ok':
            return resultWrapper('ok', {'token': result['token']}, '')

def accountGetUserList(uid):
    """
    params, uid:(int)uid
    return, data: {'count':(int)count, 'users':[{'uid':(int)uid, 'username':(string)username}...]}
    """ 
    #If users exist in database, return all of them or return error
    if not Users.objects():
        rmsg, rdata, rstatus = 'no user found!', {}, 'error'
    else:
        rmsg, rstatus = '', 'ok'
        users = [{'uid': d['uid'], 'username': d['username']} for d in Users.objects()]
        rdata = {'count': len(users), 'users': users}
    return resultWrapper(rstatus, rdata, rmsg)

def accountGetInfo(uid):
    """
    params, uid:(int)uid
    return, data: {'uid':(int)uid, 'username':(string)username, 'info': (dict)userinfo}
    """ 
    #If uid exists, return its username and info, or return error.
    result = Users.objects(uid=uid)
    if not result:
        rmsg, rdata, rstatus = 'Invalid User ID!!', {}, 'error'
    else:
        useraccount = result.first()
        uinfo = {'uid': uid, 'username': useraccount.username, 'info': useraccount.info.__dict__['_data'], 'avatar': useraccount.avatar}
        rdata = {'userinfo': uinfo}
        rmsg, rstatus = '', 'ok'
    return resultWrapper(rstatus, rdata, rmsg)

def accountGetGroups(uid):
    """
    params, uid:(int)uid
    return, data: {'groups':[{'gid':(int)gid1,'groupname':(string)name1, 'allsession': (int)count, 'livesession': (int)count},...]}
    """ 
    result = Users.objects(uid=uid)
    if not result:
        rmsg, rdata, rstatus = 'Invalid User ID!!', {}, 'error'
    else:
        usergroup = []
        group = GroupMembers.objects(uid=uid)
        if group:
            for g in group:
                ownerid = GroupMembers.objects(role=10, gid=g.gid).first().uid
                ownername = Users.objects(uid=ownerid).first().username
                targetgroupname = Groups.objects(gid=g.gid).first().groupname
                usergroup.append({'gid': g.gid, 'groupname': targetgroupname,
                                  'userrole': g.role, 'groupowner': ownername,
                                  'allsession': len(session.objects(gid=g.gid)),
                                  'livesession': len(session.objects(gid=g.gid, endtime=''))})
        return resultWrapper('ok', {'usergroup': usergroup}, '')

def accountGetSessions(uid):
    """
    params, uid:(int)uid
    return, data: {'sessions': [{'sid':(int)sid, 'gid':(int)gid, 'groupname':(string)name},...]}
    """ 
    result = Users.objects(uid=uid)
    if not result:
        rmsg, rdata, rstatus = 'Invalid User ID!!', {}, 'error'
    else:
        usersession = []
        sessions = Sessions.objects(uid=uid)
        if sessions:
            for s in sessions:
                usersession.append({'sid': s.sid, 'gid': s.gid, 'groupname': groups.objects(gid=gid).first().groupname})
        return resultWrapper('ok' ,{'usersession': usersession}, '')