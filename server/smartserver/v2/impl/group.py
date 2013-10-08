#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper
from db import groups, user, usetoken
import json

ROLES_M = {'owner': 0, 'admin': 1, 'member': 2}
ROLES = ['owner', 'admin', 'member']

def groupCreate(data):
    """
    params, data: {'token':(string)token, 'groupname':(string)name} 
    return, data: {'gid':(int)gid}
    """
    #If groupname has been regitered already, return error
    uid = list(usetoken.objects(token = data['token']))[0].uid
    if len(list(groups.objects(groupname = data['groupname']))) != 0:
        return resultWrapper('A group with same username exists!', {'code': '04'}, 'error')
    #Save group and set current user as its owner.
    groupInst = groups().from_json(json.dumps({'groupname': data['groupname'], 'members': [{'uid': uid, 'role': ROLES_M['owner']}]}))
    try:
        groupInst.save()
    except OperationError:
        return resultWrapper('save group failed', {}, 'error')
    gid = list(groups.objects(groupname = data['groupname']))[0].gid
    return resultWrapper('', {'gid': gid}, 'ok')

def __CheckUserRole(token, gid):
    uid = list(usetoken.objects(token = token))[0].uid
    Members = list(groups.objects(gid = gid, members__uid = uid))[0].members
    for member in Members:
        if (ROLES[member.role] != 'owner') & (ROLES[member.role] != 'admin'):
            return 0
        else:
            return 1

def groupDelete(data):
    """
    params, data: {'token':(string)token, 'gid':(gid)groupid} 
    return, data: {'gid':(int)gid}
    """
    #If current user is admin or owner, permit delete or return error.
    if not __CheckUserRole(data['token'], data['gid']):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        try:
            groups.objects(gid = data['gid']).delete()
            #TODO: Add a task to remove corresponding data of a group
        except OperationError:
            return resultWrapper('Remove group failed!', {}, 'error')
        return resultWrapper('', {}, 'ok')

def addGroupMembers(data, gid):
    """
    params, data: {'token':(string)token, 'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit add member or return error.
    if not __CheckUserRole(data['token'], gid):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        try:
            groups.objects(gid = gid).update(push_all__members=data['members'])
        except OperationError:
            return resultWrapper('Add member failed!', {}, 'error')
        return resultWrapper('', {}, 'ok')

def setGroupMembers(data, gid):
    """
    params, data: {'token':(string)token, 'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit set member role or return error.
    if not __CheckUserRole(data['token'], gid):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        for member in data['members']:
            if len(list(groups.objects(gid = gid, members__uid = member['uid']))) == 0:
                return resultWrapper('This user have not been added to currect group yet!', {}, 'error')
            else:
                try:
                    groups.objects(gid = gid, members__uid = member['uid']).update(set__members__S__role = member['role'])
                except OperationError:
                    return resultWrapper('Set user role failed!', {'code': '04'}, 'error')
        return resultWrapper('', {}, 'ok')    

def delGroupMembers(data, gid):
    """
    params, data: {'token':(string)token, 'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit remove member or return error.
    if not __CheckUserRole(data['token'], gid):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        for member in data['members']:
            if len(list(groups.objects(gid = gid, members__uid = member['uid']))) == 0:
                return resultWrapper('This user does not belong to currect group!', {}, 'error')
            else:
                try:
                    groups.objects(gid = gid).update(pop__members__S__uid = member['uid'])
                except OperationError:
                    return resultWrapper('Remove user failed!', {'code': '04'}, 'error')
        return resultWrapper('', {}, 'ok')

def groupGetInfo(data, gid):
    """
    params, data: {'token':(string)token}
    return, data: {'members':[{'uid':(int)uid, 'role':(String)role, 'username':(String)username, 'info':(JSON)info},...]}
    """
    #If current user is a member, return all members' info of current group, or return error.
    Members = []
    uid = list(usetoken.objects(token = data['token']))[0].uid
    if len(list(groups.objects(gid = gid, members__uid = uid))) == 0:
        return resultWrapper('Member permission required!', {'code':'00'}, 'error')
    else:
        for member in list(groups.objects(gid = gid))[0].members:
            User = user.objects(uid = member.uid).first()
            Members.append({
                'uid': member.uid,
                'role': ROLES[member.role],
                'username': User.username,
                'info': User.info.__dict__['_data']
                })
        return resultWrapper('', {'members': Members}, 'ok')

def groupGetSessionsSummary(data, gid):
    pass