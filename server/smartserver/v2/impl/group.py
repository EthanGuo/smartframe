#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper
from mongoengine import OperationError
from db import Groups, Users, Cycles, Sessions, GroupMembers
from ..config import TIME_FORMAT
import json

ROLES = {'OWNER': 10, 'ADMIN': 9, 'MEMBER': 8, 'GUEST': 7}

def groupCreate(data, uid):
    """
    params, data: {'groupname':(string), 'info':(string)}
    return, data: {'gid':(int)gid}
    """
    #If groupname has been registered already, return error
    if Groups.objects(groupname=data.get('groupname')):
        return resultWrapper('error', {}, 'A group with same username exists!')
    #Save group and set current user as its owner.
    groupInst = Groups().from_json(json.dumps({'groupname': data['groupname'], 'info': data.get('info', '')}))
    try:
        groupInst.save()
        gid = Groups.objects(groupname=data['groupname']).first().gid
        memberInst = GroupMembers().from_json(json.dumps({'uid': int(uid), 'role': ROLES['OWNER'], 'gid': gid}))
        memberInst.save()
    except OperationError:
        return resultWrapper('error', {}, 'save group failed')
    return resultWrapper('ok', {'gid': gid}, '')

def __getUserRole(uid, gid):
    g = GroupMembers.objects(gid=gid, uid=uid).first()
    if g:
        return g.role
    else:
        return -1 # Invalide gid

def groupDelete(data, gid, uid):
    """
    params, data: {} 
    return, data: {}
    """
    #If current user is admin or owner, permit delete or return error.
    gid, uid = int(gid), int(uid)
    if __getUserRole(uid, gid) < 10:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        try:
            Groups.objects(gid=gid).delete()
            GroupMembers.objects(gid=gid).delete()
        except OperationError:
            return resultWrapper('error', {}, 'Remove group failed!')
        #TODO: Add a task to remove corresponding data of a group
        return resultWrapper('ok', {}, '')

def groupSetMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, continue or return error.
    gid, uid = int(gid), int(uid)
    if __getUserRole(uid, gid) < 9:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        for member in data.get('members'):
            if member['role'] == 10:
                return resultWrapper('error', {}, 'There should be only one owner!')
            target = GroupMembers.objects(gid=gid, uid=member['uid']).first()
            try:
                #If target exists in current group, modify its role.
                if target:
                    if target.role == 10:
                        return resultWrapper('error', {}, 'Can not modify owner permission!')
                    else:
                        GroupMembers.objects(gid=gid, uid=member['uid']).update(set__role=member['role'])
                #If target does not exist in current group, save it to current group.
                else:
                    memberInst = GroupMembers().from_json(json.dumps({'gid': gid, 'uid': member['uid'], 'role': member['role']}))
                    memberInst.save()
            except OperationError:
                return resultWrapper('error', {}, 'Operation failed!')
        return resultWrapper('ok', {}, '')    

def groupDelMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, permit remove member or return error.
    gid, uid = int(gid), int(uid)
    if __getUserRole(uid, gid) < 9:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        for member in data.get('members'):
            try:
                GroupMembers.objects(gid=gid, uid=member['uid']).delete()
            except OperationError:
                return resultWrapper('error', {}, 'Remove user failed!')
        return resultWrapper('ok', {}, '')

def groupGetMembers(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'members':[{'uid':(int)uid, 'role':(String)role, 'username':(String)username, 'info':(JSON)info},...]}
    """
    #If current user is a member, return all members' info of current group, or return error.
    gid = int(gid)
    groupMembers = []
    for member in GroupMembers.objects(gid=gid):
        User = Users.objects(uid=member.uid).first()
        groupMembers.append({
            'uid': member.uid,
            'role': member.role,
            'username': User.username,
            'info': User.info.__dict__['_data']
            })
    return resultWrapper('ok', {'members': groupMembers}, '')

def groupGetSessions(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'sessions':[{'gid':(int)gid, 'product':(String)product, 
                                'revision':(String)revision, 'deviceid':(string)deviceid,
                                'starttime': (String)time, 'endtime': (String)time,
                                'runtime': (int)time, 'tester': (String)name},...]}
    """
    gid, sessions = int(gid), []
    for session in Sessions.objects(gid=gid):
        if session.deviceinfo:
            product = session.deviceinfo.product
            revision = session.deviceinfo.revision
            deviceid = session.deviceinfo.deviceid
        else:
            product, revision, deviceid = '', '', ''
        user = Users.objects(uid=session.uid).first()
        tester = user.username if user else ''
        sessions.append({'gid': gid, 'product': product, 'revision': revision,
                         'deviceid': deviceid, 
                         'starttime': session.starttime.strftime(TIME_FORMAT),
                         'endtime': session.endtime.strftime(TIME_FORMAT), 
                         'runtime': session.runtime, 'tester': tester})
    return resultWrapper('ok', {'sessions': sessions}, '')

def groupGetCycles(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'sessions':[{'cid': (int)cid, 'product': (string)product, 'revision': (string)revision,
                                'livecount': (int)num, 'devicecount': (int)num},...]}
    """
    gid, cycles, i = int(gid), [], 0
    for cycle in Cycles.objects(gid=gid):
        cycles.append({'cid': cycle.cid, 'devicecount': 0, 'livecount': 0, 'product': '', 'revision': ''})
        for sid in cycle.sids:
            session = Sessions.objects(sid=sid).first()
            if not cycles[i]['product']:
                if session.deviceinfo:
                    cycles[i]['product'] = session.deviceinfo.product
            if not cycles[i]['revision']:
                if session.deviceinfo:
                    cycles[i]['revision'] = session.deviceinfo.revision
            if not session.endtime:
                cycles[i]['livecount'] += 1
            cycles[i]['devicecount'] += 1
        i += 1
    return resultWrapper('ok', {'cycles': cycles}, '')

def groupGetReport(data, gid, uid):
    # data is cid itself
    pass