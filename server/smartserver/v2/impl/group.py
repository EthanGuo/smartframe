#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper
from mongoengine import OperationError
from db import groups, user
import json

ROLES = {'OWNER': 10, 'ADMIN': 9, 'MEMBER': 8, 'GUEST': 7}

def groupCreate(data, uid):
    """
    params, data: {'groupname':(string)name} 
    return, data: {'gid':(int)gid}
    """
    #If groupname has been registered already, return error
    if len(groups.objects(groupname = data['groupname'])) != 0:
        return resultWrapper('error', {}, 'A group with same username exists!')
    #Save group and set current user as its owner.
    groupInst = groups().from_json(json.dumps({'groupname': data['groupname'], 'members': [{'uid': uid, 'role': ROLES['OWNER']}]}))
    try:
        groupInst.save()
    except OperationError:
        return resultWrapper('error', {}, 'save group failed')
    gid = groups.objects(groupname = data['groupname']).first().gid
    return resultWrapper('ok', {'gid': gid}, '')

def __getUserRole(uid, gid):
    g = groups.objects(gid = gid).first()
    if g:
        groupMembers = g.members
        for member in groupMembers:
            if (member.uid) == uid:
                return member.role
    else:
        return -1 # Invalide gid

def groupDelete(data, uid):
    """
    params, data: {'gid':(gid)groupid} 
    return, data: {}
    """
    #If current user is admin or owner, permit delete or return error.
    if __getUserRole(uid, data['gid']) < 10:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        try:
            groups.objects(gid = data['gid']).delete()
            #TODO: Add a task to remove corresponding data of a group
        except OperationError:
            return resultWrapper('error', {}, 'Remove group failed!')
        return resultWrapper('ok', {}, '')

def addGroupMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit add member or return error.
    gid = int(gid)
    if __getUserRole(uid, gid) < 9:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        try:
            groups.objects(gid = gid).update(push_all__members=data['members'])
        except OperationError:
            return resultWrapper('error', {}, 'Add member failed!')
        return resultWrapper('ok', {}, '')

def setGroupMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit set member role or return error.
    gid = int(gid)
    if __getUserRole(uid, gid) < 9:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        for member in data['members']:
            if len(groups.objects(gid = gid, members__uid = member['uid'])) == 0:
                return resultWrapper('error', {}, 'This user have not been added to currect group yet!')
            else:
                try:
                    groups.objects(gid = gid, members__uid = member['uid']).update(set__members__S__role = member['role'])
                except OperationError:
                    return resultWrapper('error', {}, 'Set user role failed!')
        return resultWrapper('ok', {}, '')    

def delGroupMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit remove member or return error.
    gid = int(gid)
    if __getUserRole(uid, gid) < 9:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        for member in data['members']:
            try:
                groups.objects(gid = gid).update(pull__members = {'uid':member['uid'], 'role': member['role']})
            except OperationError:
                return resultWrapper('error', {}, 'Remove user failed!')
        return resultWrapper('ok', {}, '')

def groupGetInfo(gid, uid):
    """
    params, data: {}
    return, data: {'members':[{'uid':(int)uid, 'role':(String)role, 'username':(String)username, 'info':(JSON)info},...]}
    """
    #If current user is a member, return all members' info of current group, or return error.
    gid = int(gid)
    groupMembers = []
    for member in groups.objects(gid = gid).first().members:
        User = user.objects(uid = member.uid).first()
        groupMembers.append({
            'uid': member.uid,
            'role': member.role,
            'username': User.username,
            'info': User.info.__dict__['_data']
            })
    return resultWrapper('ok', {'members': groupMembers}, '')

def groupGetSessionsSummary(gid, uid):
    pass