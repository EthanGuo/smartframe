#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper
from mongoengine import OperationError
from db import groups, user
import json

ROLES = {'owner': 0, 'admin': 1, 'member': 2}

def groupCreate(data, uid):
    """
    params, data: {'groupname':(string)name} 
    return, data: {'gid':(int)gid}
    """
    #If groupname has been registered already, return error
    if len(groups.objects(groupname = data['groupname'])) != 0:
        return resultWrapper('A group with same username exists!', {'code': '04'}, 'error')
    #Save group and set current user as its owner.
    groupInst = groups().from_json(json.dumps({'groupname': data['groupname'], 'members': [{'uid': uid, 'role': ROLES['owner']}]}))
    try:
        groupInst.save()
    except OperationError:
        return resultWrapper('save group failed', {}, 'error')
    gid = groups.objects(groupname = data['groupname']).first().gid
    return resultWrapper('', {'gid': gid}, 'ok')

def __CheckUserRole(uid, gid):
    Members = groups.objects(gid = gid, members__uid = uid).first().members
    for member in Members:
        if (member.uid) == uid:
            if (ROLES.keys()[member.role] == 'owner') or (ROLES.keys()[member.role] == 'admin'):
                return 1
    return 0

def groupDelete(data, uid):
    """
    params, data: {'gid':(gid)groupid} 
    return, data: {}
    """
    #If current user is admin or owner, permit delete or return error.
    if not __CheckUserRole(uid, data['gid']):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        try:
            groups.objects(gid = data['gid']).delete()
            #TODO: Add a task to remove corresponding data of a group
        except OperationError:
            return resultWrapper('Remove group failed!', {}, 'error')
        return resultWrapper('', {}, 'ok')

def addGroupMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit add member or return error.
    gid = int(gid)
    if not __CheckUserRole(uid, gid):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        try:
            groups.objects(gid = gid).update(push_all__members=data['members'])
        except OperationError:
            return resultWrapper('Add member failed!', {}, 'error')
        return resultWrapper('', {}, 'ok')

def setGroupMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit set member role or return error.
    gid = int(gid)
    if not __CheckUserRole(uid, gid):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        for member in data['members']:
            if len(groups.objects(gid = gid, members__uid = member['uid'])) == 0:
                return resultWrapper('This user have not been added to currect group yet!', {}, 'error')
            else:
                try:
                    groups.objects(gid = gid, members__uid = member['uid']).update(set__members__S__role = member['role'])
                except OperationError:
                    return resultWrapper('Set user role failed!', {'code': '04'}, 'error')
        return resultWrapper('', {}, 'ok')    

def delGroupMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit remove member or return error.
    gid = int(gid)
    if not __CheckUserRole(uid, gid):
        return resultWrapper('Admin permission required!', {'code':'00'}, 'error')
    else:
        for member in data['members']:
            if len(groups.objects(gid = gid, members__uid = member['uid'])) == 0:
                return resultWrapper('This user does not belong to currect group!', {}, 'error')
            else:
                try:
                    groups.objects(gid = gid).update(pull__members = {'uid':member['uid'], 'role': member['role']})
                except OperationError:
                    return resultWrapper('Remove user failed!', {'code': '04'}, 'error')
        return resultWrapper('', {}, 'ok')

def groupGetInfo(gid, uid):
    """
    params, data: {}
    return, data: {'members':[{'uid':(int)uid, 'role':(String)role, 'username':(String)username, 'info':(JSON)info},...]}
    """
    #If current user is a member, return all members' info of current group, or return error.
    gid = int(gid)
    Members = []
    if len(groups.objects(gid = gid, members__uid = uid)) == 0:
        return resultWrapper('Member permission required!', {'code':'00'}, 'error')
    else:
        for member in groups.objects(gid = gid).first().members:
            User = user.objects(uid = member.uid).first()
            Members.append({
                'uid': member.uid,
                'role': member.role,
                'username': User.username,
                'info': User.info.__dict__['_data']
                })
        return resultWrapper('', {'members': Members}, 'ok')

def groupGetSessionsSummary(gid, uid):
    pass