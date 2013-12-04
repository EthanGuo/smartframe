#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib, uuid
import string, json
from random import choice
from sendmail import *
from util import resultWrapper
from mongoengine import OperationError, DoesNotExist
from db import Users, UserTokens, Groups, Sessions, GroupMembers
from filedealer import saveFile, deleteFile
from ..tasks import ws_send_activeaccount_mail, ws_send_retrievepswd_mail, ws_send_invitation_mail
import time

TOKEN_EXPIRES = {'01': 30*24*3600, #For client end upload result purpose 
                 '02': 7*24*3600, #For browser user.
                 '03': 24*3600, #For user to active itself by email. 
                 }

def createToken(appid, uid):
    """
    Create a token, add it to mongodb, return the token generated.
    """
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    token = m.hexdigest()
    tokenInst = UserTokens(token=token, appid=appid, uid=uid, expires=(TOKEN_EXPIRES[appid] + time.time()))
    try:
        tokenInst.save()
        return {'status': 'ok', 'token': token}
    except OperationError:
        return {'status': 'error'}

def accountValidToken(token):
    try:
        usertoken = UserTokens.objects.get(token=token)
        return usertoken.uid
    except DoesNotExist:
        return None

def accountLogin(data):
    """
    params, data: {'appid':(string), 'username':(string), 'password':(string)}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    #Check whether data['username'] is username or email address.
    #Find user by email/password or username/password
    if '@' in data.get('username'):
        result = Users.objects(info__email=data['username'], password=data['password']).only('active', 'appid', 'uid')
    else:
        result = Users.objects(username=data['username'], password=data['password']).only('active', 'appid', 'uid')
    #If user exists, create a token for it and return, or return error.
    if len(result) != 0:
        useraccount = result.first()
        #Check the active status of user here, if not activated, forbit login.
        if not useraccount.active:
            return resultWrapper('error', {}, 'Your account has not been activated yet!')
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
                   'info':{'email':(string), 'telephone':(string), 'company':(string)},
                   'baseurl': (string)}
    return, data: {'token':(string)token, 'uid':(int)uid}
    """
    # If both username and email have not been registered, create a new user, generate a token, send a mail then return, or return error.
    if (not Users.objects(username=data['username']).only('uid')) and (not Users.objects(info__email=data['info']['email']).only('uid')):
        try:
            userInst = Users().from_json(json.dumps(data))
            userInst.save()
        except OperationError:
            return resultWrapper('error', {}, 'Save user failed!')
        ret = createToken(appid=userInst.appid, uid=userInst.uid)
        if ret['status'] == 'ok':
            rmsg, rdata, rstatus = '', {'token': ret['token'], 'uid': userInst.uid}, 'ok'
            ws_send_activeaccount_mail.delay(userInst.info.email, userInst.username, ret['token'], data['baseurl'])
        else:
            rmsg, rdata, rstatus = 'Create token failed!', {}, 'error'
    else:
        rmsg, rdata, rstatus = 'An account with same email or username already registered!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def accountRetrievePasswd(data):
    """
    params, data: {'email':(string)mailaddress, 'baseurl':(string)url}
    return, data: {}
    """    
    # Find user by email, if user exists, update its password, generate a token, then send mail to it, or return error.
    result = Users.objects(info__email=data.get('email')).only('uid')
    if len(result) == 1:
        newpassword = ''.join([choice(string.ascii_letters + string.digits) for i in range(8)])
        m = hashlib.md5()
        m.update(newpassword)
        m.hexdigest()
        useraccount = result.first()
        try:
            useraccount.update(set__password=m.hexdigest())
            useraccount.reload()
        except OperationError:
            return resultWrapper('error', {}, 'Save new password failed!')
        #Send mail to user with the new password.
        ws_send_retrievepswd_mail.delay(data['email'], newpassword, data['baseurl'])
        rmsg, rdata, rstatus = '', {}, 'ok' 
    else:
        rmsg, rdata, rstatus = 'Invalid email!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def accountChangepasswd(data, token, uid):
    """
    params, data: {'oldpassword':(string)oldpassword, 'newpassword':(string)newpassword}
    return, data: {}
    """  
    #Find user by user uid and oldpassword
    result = Users.objects(uid=uid, password=data.get('oldpassword')).only('uid')
    #If user exist, update its password, or return error
    if len(result) == 1:
        try:
            useraccount = result.first()
            useraccount.update(set__password=data.get('newpassword'))
            useraccount.reload()
            rmsg, rdata, rstatus = '', {}, 'ok'
        except OperationError:
            rmsg, rdata, rstatus = 'Save new password failed!', {}, 'error'
    else:
        rmsg, rdata, rstatus = 'Incorrect original password!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def accountInvite(data, token, uid):
    """
    params, data: {'email':(string)email, 'username':(string)username, 'baseurl':(string)url}
    return, data: {}
    """ 
    #Send a mail to the invited user.
    orguser = Users.objects(uid=uid).only('username').first().username
    ws_send_invitation_mail.delay(data['email'], data['username'], orguser, data['baseurl'])
    return resultWrapper('ok', {}, '')

def accountLogout(data, token, uid):
    """
    params, data: {}
    return, data: {}
    """ 
    #Remove the token then return
    try:
        UserTokens.objects(token=token).delete()
        rmsg, rdata, rstatus = '', {}, 'ok'
    except OperationError:
        rmsg, rdata, rstatus = 'Remove token failed!', {}, 'error'
    return resultWrapper(rstatus, rdata, rmsg)

def __updateAvatar(data, uid):
    """
       Update avatar here
    """
    filetype = data['file'].filename.split('.')[-1].lower()
    if not filetype in ['png', 'jpg', 'jpeg']:
        return resultWrapper('error', {}, 'Support png/jpg/jpeg image only!')
    filedata = data['file'].file
    u = Users.objects(uid=uid).only('avatar').first()
    if u.avatar:
        fileid = u.avatar['url'].strip().replace('/file/', '')
        deleteFile(fileid)
    imageurl = saveFile(filedata, 'image/' + filetype, data['file'].filename)
    try:
        u.update(set__avatar={'filename': data['file'].filename, 'url': imageurl})
        u.reload()
    except OperationError:
        return resultWrapper('error', {}, 'Update avatar failed!')
    return resultWrapper('ok', {'filename': data['file'].filename, 'url': imageurl}, 'Upload successfully!')

def accountUpdate(data, token, uid):
    """
    params, data: {'appid': (string)appid, 'username': (string)username, 'company': (string)company, 'telephone': (string)phone, 'file': (dict)file}
    return, data: {'token': (string)token}
    """ 
    if 'file' in data.keys():
        return __updateAvatar(data, uid)
    else:
        useraccount = Users.objects(uid=uid).only('username', 'info').first()
        try:
            if data.has_key('username'):
                if Users.objects(username=data['username']).first():
                    return resultWrapper('error', {}, 'This name has been taken already!')
                useraccount.update(set__username=data['username'])
                useraccount.reload()
            if data.has_key('company'):
                useraccount.update(set__info__company=data['company'])
                useraccount.reload()
            if data.has_key('telephone'):
                useraccount.update(set__info__phonenumber=data['telephone'])
                useraccount.reload()
        except OperationError:
            return resultWrapper('error', {}, 'Update user info failed!')
        result = createToken(data['appid'], uid)
        if result['status'] == 'ok':
            return resultWrapper('ok', {'token': result['token']}, '')
        else:
            return resultWrapper('error', {}, 'Generate token failed!')

def accountGetUserList(uid):
    """
    params, uid:(int)uid
    return, data: {'count':(int)count, 'users':[{'uid':(int)uid, 'username':(string)username}...]}
    """ 
    #If users exist in database, return all of them or return error
    users = Users.objects().only('uid', 'username')
    if not len(users):
        return resultWrapper('error', {}, 'no user found!')
    else:
        ret = [{'uid': user.uid, 'username': user.username} for user in users]
        return resultWrapper('ok', {'count': len(ret), 'users': ret}, '')

def accountGetInfo(uid):
    """
    params, uid:(int)uid
    return, data: {'uid':(int)uid, 'username':(string)username, 'info': (dict)userinfo, 'avatar':(dict)}
    """ 
    #Return uid's username and info.
    result = Users.objects(uid=uid).only('username', 'info', 'avatar')
    useraccount = result.first()
    uinfo = {'uid': uid, 'username': useraccount.username, 'info': useraccount.info.__dict__['_data'], 'avatar': useraccount.avatar}
    return resultWrapper('ok', {'userinfo': uinfo}, '')

def accountGetGroups(uid):
    """
    params, uid:(int)uid
    return, data: {'usergroup':[{'gid':(int)gid1,'groupname':(string)name1, 'allsession': (int)count, 'livesession': (int)count},...]}
    """ 
    usergroup = []
    group = Groups.objects()
    if group:
        for g in group:
            product = []
            for session in Sessions.objects(gid=g.gid).only('deviceinfo'):
                if not session.deviceinfo.product in product:
                    product.append(session.deviceinfo.product)
            userrole = 8
            for member in GroupMembers.objects(gid=g.gid):
                if member.role == 10:
                    ownerid = member.uid
                if member.uid == uid:
                    userrole = member.role
            ownername = Users.objects(uid=ownerid).only('username').first().username
            targetgroupname = Groups.objects(gid=g.gid).only('groupname').first().groupname
            usergroup.append({'gid': g.gid, 'groupname': targetgroupname,
                              'userrole': userrole, 'groupowner': ownername,
                              'product': product, 'info': g.info})
    return resultWrapper('ok', {'usergroup': usergroup}, '')

def accountGetSessions(uid):
    """
    params, uid:(int)uid
    return, data: {'usersession': [{'sid':(String)sid, 'gid':(int)gid, 'groupname':(string)name},...]}
    """ 
    usersession = []
    sessions = Sessions.objects(uid=uid).only('sid', 'gid')
    if sessions:
        for s in sessions:
            usersession.append({'sid': s.sid, 'gid': s.gid, 'groupname': Groups.objects(gid=s.gid).only('groupname').first().groupname})
    return resultWrapper('ok' ,{'usersession': usersession}, '')

def accountActiveUser(uid):
    """
       Active current user and remove the original token
    """
    try:
        Users.objects(uid=uid).only('active').update(set__active=True)
    except OperationError:
        Users.objects(uid=uid).only('active').update(set__active=True)
    result = accountLogout({}, uid)
    if result['result'] != 'ok':
        accountLogout({}, uid)
    result = "<script>alert(\"Your account has been activated successfully!\");\
    window.location = window.location.protocol + \"//\" + window.location.hostname + \
    (window.location.port ? \":\" + window.location.port : \"\") + \"/smartserver\"</script>"
    return result