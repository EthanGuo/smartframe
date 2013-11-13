#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper
from mongoengine import OperationError
from db import Groups, Users, Cycles, Sessions, GroupMembers, Cases
from ..config import TIME_FORMAT
from ..tasks import ws_del_group
import json

ROLES = {'OWNER': 10, 'ADMIN': 9, 'MEMBER': 8, 'GUEST': 7}

def groupCreate(data, uid):
    """
    params, data: {'groupname':(string), 'info':(string)}
    return, data: {'gid':(int)gid}
    """
    #If groupname has been registered already, return error
    if Groups.objects(groupname=data.get('groupname')).only('gid'):
        return resultWrapper('error', {}, 'A group with same username exists!')
    #Save group and set current user as its owner.
    groupInst = Groups().from_json(json.dumps({'groupname': data['groupname'], 'info': data.get('info', '')}))
    try:
        groupInst.save()
        memberInst = GroupMembers().from_json(json.dumps({'uid': int(uid), 'role': ROLES['OWNER'], 'gid': groupInst.gid}))
        memberInst.save()
    except OperationError:
        return resultWrapper('error', {}, 'save group failed')
    return resultWrapper('ok', {'gid': groupInst.gid}, '')

def __getUserRole(uid, gid):
    g = GroupMembers.objects(gid=gid, uid=uid).only('role').first()
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
            Cycles.objects(gid=gid).delete()
        except OperationError:
            return resultWrapper('error', {}, 'Remove group failed!')
        ws_del_group(gid)
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
            target = GroupMembers.objects(gid=gid, uid=member['uid']).only('role').first()
            try:
                #If target exists in current group, modify its role.
                if target:
                    if target.role == 10:
                        return resultWrapper('error', {}, 'Can not modify owner permission!')
                    elif target.role == member['role']:
                        return resultWrapper('error', {}, 'Member has been added to this group already!')
                    else:    
                        target.update(set__role=member['role'])
                        target.reload()
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
                groupmember = GroupMembers.objects(gid=gid, uid=member['uid']).only('role').first()
                if not groupmember:
                    return resultWrapper('error', {}, 'Invalid user!')
                else:
                    if groupmember.role == 10:
                        return resultWrapper('error', {}, 'Can not remove group owner from the group!')
                groupmember.delete()
            except OperationError:
                return resultWrapper('error', {}, 'Remove user failed!')
        return resultWrapper('ok', {}, '')

def groupGetMembers(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'members':[{'uid':(int)uid, 'role':(String)role, 'username':(String)username, 'avatar':(Dict),'info':(JSON)info},...]}
    """
    #If current user is a member, return all members' info of current group, or return error.
    gid = int(gid)
    groupMembers = []
    for member in GroupMembers.objects(gid=gid):
        User = Users.objects(uid=member.uid).only('username', 'info', 'avatar').first()
        groupMembers.append({
            'uid': member.uid,
            'role': member.role,
            'username': User.username,
            'avatar': User.avatar,
            'info': User.info.__dict__['_data']
            })
    return resultWrapper('ok', {'members': groupMembers}, '')

def groupGetSessions(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'sessions':[{'gid':(int)gid, 'product':(String)product, 'sid': (String),
                                'revision':(String)revision,
                                'starttime': (String)time, 'endtime': (String)time, 'cid': (int)
                                'tester': (String)name},...]}
    """
    gid, sessions = int(gid), []
    for session in Sessions.objects(gid=gid).only('deviceinfo', 'uid', 'sid', 'starttime', 'endtime'):
        if session.deviceinfo:
            product = session.deviceinfo.product
            revision = session.deviceinfo.revision
        else:
            product, revision = '', ''
        user = Users.objects(uid=session.uid).only('username').first()
        tester = user.username if user else ''
        endtime = session.endtime.strftime(TIME_FORMAT) if session.endtime else ''
        cycle = Cycles.objects(sids=session.sid).only('cid').first()
        cid = cycle.cid if cycle else ''
        sessions.append({'gid': gid, 'product': product, 'revision': revision,
                         'sid': session.sid,
                         'starttime': session.starttime.strftime(TIME_FORMAT),
                         'endtime': endtime, 'cid': cid, 'tester': tester})
    return resultWrapper('ok', {'sessions': sessions}, '')

def groupGetCycles(data, gid, uid):
    """
    params, data: {'cid' is contained but wont be used here}
    return, data: {'sessions':[{'cid': (int)cid, 'product': (string)product, 'revision': (string)revision,
                                'livecount': (int)num, 'devicecount': (int)num},...]}
    """
    gid, cycles, i = int(gid), [], 0
    for cycle in Cycles.objects(gid=gid).only('cid', 'sids'):
        cycles.append({'cid': cycle.cid, 'devicecount': 0, 'livecount': 0, 'product': '', 'revision': ''})
        for sid in cycle.sids:
            session = Sessions.objects(sid=sid).only('deviceinfo', 'endtime').first()
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

def __calculateResult(sessionresult):
    """
       Return the data frontend required.
    """
    table1, table2, table3, table4, i = {}, {}, {}, {}, 1
    table1['totalfailure'], table1['totaluptime'] = 0, 0
    table1['devicecount'] = len(sessionresult)
    table1['mtbf'] = ''

    for session in sessionresult:
        if not table1.get('product'):
            table1['product'] = session['product']
        if not table1.get('revision'):
            table1['revision'] = session['revision']
        table1['totalfailure'] += session['failurecount']
        table1['totaluptime'] += session['totaluptime']

        for issue in session['issues']:
            if issue['issueType'] in table2.keys():
                table2[issue['issueType']] += 1
            else:
                table2.update({issue['issueType']: 1})

        if session['deviceid']:
            deviceid = session['deviceid']
        else:
            deviceid = 'device_' + str(i)
            i += 1
        table3[deviceid] = {'starttime': session['starttime'], 'endtime': session['endtime'],
                            'failurecount': session['failurecount'], 'firstuptime': session['firstuptime'],
                            'uptime': session['totaluptime'], 'issues': session['issues'], 'sid': session['sid']}

        for casename in session['domains'].keys():
            domain = casename.strip().split('.')[0]
            if domain in table4.keys():
                if casename in table4[domain].keys():
                    table4[domain][casename]['pass'] += session['domains'][casename]['pass']
                    table4[domain][casename]['fail'] += session['domains'][casename]['fail']
                    table4[domain][casename]['block'] += session['domains'][casename]['block']
                else:
                    table4[domain][casename] = session['domains'][casename]
            else:
                table4[domain] = {casename: session['domains'][casename]}
    
    return resultWrapper('ok', {'table1': table1, 'table2': table2, 
                                'table3': table3, 'table4': table4}, '')

def groupGetReport(data, gid, uid):
    """
    params, data: {'cid'}
    return, data: report data
    """
    gid, cid, sessionresult = int(gid), int(data), []
    cycle = Cycles.objects(cid=cid).first()
    if not cycle:
        return resultWrapper('error', {}, 'Invalid cycle id!')
    for sid in cycle.sids:
        session = Sessions.objects(gid=gid, sid=sid).first()
        cases = Cases.objects(sid=sid).order_by('+tid')
        if session.deviceinfo:
            deviceid = session.deviceinfo.deviceid
            revision = session.deviceinfo.revision
            product = session.deviceinfo.product
        else:
            deviceid, revision, product = '', '', ''
        starttime = session.starttime
        endtime = session.endtime
        if not endtime:
            index = len(cases) - 1
            endtime = cases[index].endtime if cases[index].endtime else cases[index].starttime
        failurecount, firstfailureuptime, blocktime, issues = 0, 0, 0, []
        for case in cases:
            if case.comments:
                if case['comments']['caseresult'] == 'fail':
                    failurecount += 1
                    issues.append({'casename': case.casename, 'starttime': case.starttime.strftime(TIME_FORMAT),
                                   'issueType': case['comments']['issuetype'], 'comments': case['comments']['commentinfo']})
                    if not firstfailureuptime:
                        caseendtime = case.endtime if case.endtime else case.starttime
                        firstfailureuptime = (caseendtime - starttime).total_seconds()
                if case['comments']['caseresult'] == 'block':
                    if case.endtime:
                        blocktime += (case.endtime - case.starttime).total_seconds()
                if case['comments']['endsession'] == 1:
                    endtime = case.endtime if case.endtime else case.starttime
                    break
        totaluptime = (endtime - starttime).total_seconds() - blocktime
        sessionresult.append({'deviceid': deviceid, 'product': product, 'revision': revision,
                              'starttime': starttime.strftime(TIME_FORMAT), 'sid': sid,
                              'endtime': endtime.strftime(TIME_FORMAT), 'failurecount': failurecount,
                              'firstuptime': firstfailureuptime, 'totaluptime': totaluptime,
                              'issues': issues, 'domains': json.loads(session.domaincount)})
    return __calculateResult(sessionresult)
