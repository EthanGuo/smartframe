#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper
from mongoengine import OperationError
from db import groups, user, cycle, session, GroupMember
import json

ROLES = {'OWNER': 10, 'ADMIN': 9, 'MEMBER': 8, 'GUEST': 7}

def groupCreate(data, uid):
    """
    params, data: {'groupname':(string)name, 'info': (string)info} 
    return, data: {'gid':(int)gid}
    """
    #If groupname has been registered already, return error
    if len(groups.objects(groupname = data['groupname'])) != 0:
        return resultWrapper('error', {}, 'A group with same username exists!')
    #Save group and set current user as its owner.
    groupInst = groups().from_json(json.dumps({'groupname': data['groupname'], 'info': data['info']}))
    try:
        groupInst.save()
        gid = groups.objects(groupname = data['groupname']).first().gid
        memberInst = GroupMember().from_json(json.dumps({'uid': int(uid), 'role': ROLES['OWNER'], 'gid': gid}))
        memberInst.save()
    except OperationError:
        return resultWrapper('error', {}, 'save group failed')
    return resultWrapper('ok', {'gid': gid}, '')

def __getUserRole(uid, gid):
    g = GroupMember.objects(gid = gid, uid=uid).first()
    if g:
        return g.role
    else:
        return -1 # Invalide gid

def groupDelete(data, uid):
    """
    params, data: {'gid':(gid)groupid} 
    return, data: {}
    """
    #If current user is admin or owner, permit delete or return error.
    if __getUserRole(int(uid), data['gid']) < 10:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        try:
            groups.objects(gid = data['gid']).delete()
            GroupMember.objects(gid=data['gid']).delete()
        except OperationError:
            return resultWrapper('error', {}, 'Remove group failed!')
        #TODO: Add a task to remove corresponding data of a group
        return resultWrapper('ok', {}, '')

def setGroupMembers(data, gid, uid):
    """
    params, data: {'members':[{'uid':(int)uid,'role':(int)roleId}]}
    return, data: {}
    """
    #If current user is admin or owner, continue or return error.
    gid = int(gid)
    if __getUserRole(uid, gid) < 9:
        return resultWrapper('error', {}, 'Permission denied!')
    else:
        for member in data['members']:
            target = GroupMember.objects(gid=gid, uid=member['uid']).first()
            try:
                #If target exists in current group, modify its role.
                if target:
                    if target.role == 10:
                        return resultWrapper('error', {}, 'Can not modify owner permission!')
                    else:
                        GroupMember.objects(gid=gid, uid=member['uid']).update(set__role=member['role'])
                #If target does not exist in current group, save it to current group.
                else:
                    memberInst = GroupMember().from_json(json.dumps({'gid': gid, 'uid': member['uid'], 'role': member['role']}))
                    memberInst.save()
            except OperationError:
                return resultWrapper('error', {}, 'Operation failed!')
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
                GroupMember.objects(gid=gid, uid=member['uid']).delete()
            except OperationError:
                return resultWrapper('error', {}, 'Remove user failed!')
        return resultWrapper('ok', {}, '')

def groupGetInfo(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'members':[{'uid':(int)uid, 'role':(String)role, 'username':(String)username, 'info':(JSON)info},...]}
    """
    #If current user is a member, return all members' info of current group, or return error.
    gid = int(gid)
    groupMembers = []
    for member in GroupMember.objects(gid=gid):
        User = user.objects(uid = member.uid).first()
        info = User.info.__dict__['_data'] if User.info else ''
        groupMembers.append({
            'uid': member.uid,
            'role': member.role,
            'username': User.username,
            'info': info
            })
    return resultWrapper('ok', {'members': groupMembers}, '')

def groupGetSessionsSummary(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'cycles': [{'cid': cycleID, 'livecount': liveDeviceCount, 'devicecount': deviceCount, 'sessions':[{},...],...]}
    """
    result = []
    sid_in_cycle = []
    cycles = cycle.objects(gid=gid)
    for c in cycles:
        sessions = []
        livecount = 0
        for sid in c.sids:
            s = session.objects(sid=sid).first()
            if not s.endtime:
                livecount += 1
            sessions.append({'gid': s.gid, 'product': s.deviceinfo.product, 
                             'revision': s.deviceinfo.revision, 'deviceid': s.deviceid,
                             'starttime': s.starttime, 'endtime': s.endtime,
                             'runtime': s.updatetime, 
                             'tester': user.objects(uid=s.uid).first().username})
            sid_in_cycle.append(sid)
        result.append({'cid': c.cid, 'livecount': livecount, 
                       'devicecount': len(c.sids),
                       'sessions': sessions})
    sessions = session.objects(gid=gid)
    sess = []
    for s in sessions:
        if not (s.sid in sid_in_cycle):
            sess.append({'gid': s.gid, 'product': s.deviceinfo.product, 
                         'revision': s.deviceinfo.revision, 'deviceid': s.deviceid,
                         'starttime': s.starttime, 'endtime': s.endtime,
                         'runtime': s.updatetime, 
                         'tester': user.objects(uid=s.uid).first().username})
    result.append({'cid': '', 'livecount': '', 
                   'devicecount': '',
                   'sessions': sess})

    return resultWrapper('ok', {'cycles': result}, '')

def groupGetCycleReport(data, gid, uid):
    # data is cid itself
    pass