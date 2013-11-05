#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db import *
from filedealer import deleteFile
import json

def sessionUpdateDomainSummary(sid, results):
    """
       Task func to update session domain count
    """
    print "Start updating the domain summary of session %s" %sid
    domaincount = json.loads(Sessions.objects(sid=sid).first().domaincount)
    for result in results:
        casename = Cases.objects(sid=sid, tid=result[0]).first().casename
        if not result[2]:
            if casename in domaincount.keys():
                domaincount[casename][result[1]] += 1
            else:
                domaincount[casename] = {'pass': 0, 'fail': 0, 'error': 0, 'block': 0}
                domaincount[casename][result[1]] += 1
        else:
            domaincount[casename][result[2]] -= 1
            domaincount[casename][result[1]] += 1
    domaincount = json.dumps(domaincount)   
    try:
        Sessions.objects(sid=sid).update(set__domaincount=domaincount)
    except OperationError:
        Sessions.objects(sid=sid).update(set__domaincount=domaincount)

def sessionActiveSession(sid):
    """
       Task function to clear session endtime if it has been set.
    """
    print "Start activate session %s" %sid
    session = Sessions.objects(sid=sid).first()
    if session.endtime:
        try:
            Sessions.objects(sid=sid).update(set__endtime='')
        except OperationError:
            Sessions.objects(sid=sid).update(set__endtime='')

def sessionSetEndTime(sid):
    """
       Task function to set session endtime.
    """
    print "Start setting the endtime of session %s" %sid
    if not Cases.objects(sid=sid):
        endtime = Sessions.objects(sid=sid).first().starttime
    else:
        case = Cases.objects(sid=sid).order_by('-tid').first()
        endtime = case.endtime if case.endtime else case.starttime

    cache.clearCache(str('sid:' + sid + ':snap'))
    cache.clearCache(str('sid:' + sid + ':snaptime'))
    try:
        Sessions.objects(sid=sid).update(set__endtime=endtime)
    except OperationError:
        Sessions.objects(sid=sid).update(set__endtime=endtime)

def caseValidateEndtime():
    """
       Used to validate case endtime
    """
    # Maybe this is not a reasonable function.
    pass

def tokenValidateExpireTime():
    """
       Used to validate token expire time and clear dirty users.
    """
    #If user has not activated itself before its token's expire time, remove this user.
    print "Start validating all the tokens of server" 
    users = Users.objects(active=False)
    for user in users:
        if (time.time() - UserTokens.objects(uid=user.uid).first().expires) <= 0:
            user.delete()
            user.reload()
    #If token has expired, remove it from database.
    for usertoken in UserTokens.objects():
        if (time.time() - usertoken.expires) <= 0:
            UserTokens.objects(token=usertoken.token).delete()

def _getID(url):
    return url.strip().replace('/file/', '')

def sessionRemoveAll(sid):
    """
       Task to remove all the cases of a session and case log/snapshots 
    """
    print "Start remove session %s" %sid
    fid = []
    for case in Cases.objects(sid=sid, result='fail'):
        if case.log:
            fid.append(_getID(case.log))
        if case.expectshot:
            fid.append(_getID(case.expectshot))
        if case.snapshots:
            for snap in case.snapshots:
                fid.append(_getID(snap))
    try:
        Cases.objects(sid=sid).delete()
    except OperationError:
        Cases.objects(sid=sid).delete()

    deleteFile(fid)

def groupRemoveAll(gid):
    """
       Task to remove all the sessions of a group.
    """
    for session in Sessions.objects(gid=gid):
        sessionRemoveAll(session.sid)
    try:
        Sessions.objects(gid=gid).delete()
    except OperationError:
        Sessions.objects(gid=gid).delete()

def _dirtyFileRemoveAll():
    #Remove dirty records in Files.
    fileids, casefileids, avatarids = [], [], []
    for f in Files.objects():
        fileids.append(f.fileid)
    for case in Cases.objects(result='fail'):
        if case.log:
            casefileids.append(_getID(case.log))
        if case.expectshot:
            casefileids.append(_getID(case.expectshot))
        if case.snapshots:
            for snap in case.snapshots:
                casefileids.append(_getID(snap))
    for user in Users.objects():
        if user.avatar:
            avatarids.append(_getID(user.avatar))

    dirtyids = fileids - casefileids - avatarids
    deleteFile(dirtyids)

def _dirtyCaseRemoveAll():
    #Remove dirty records in Cases
    casesids = Cases.objects().distinct('sid')
    sessionids = Sessions.objects().distinct('sid')

    dirtyids = casesids - sessionids
    for sid in dirtyids:
        try:
            Cases.objects(sid=sid).delete()
        except OperationError:
            Cases.objects(sid=sid).delete()

def _dirtySessionRemoveAll():
    #Remove dirty records in Sessions.
    sessiongids = Sessions.objects().distinct('gid')
    groupids = Groups.objects().distinct('gid')

    dirtyids = sessiongids - groupids
    for gid in dirtyids:
        try:
            Sessions.objects(gid=gid).delete()
        except OperationError:
            Sessions.objects(gid=gid).delete()

def _dirtyGroupMemberRemoveAll():
    #Remove dirty records in GroupMembers.
    membergids = GroupMembers.objects().distinct('gid')
    groupids = Groups.objects().distinct('gid')

    dirtyids = membergids - groupids
    for gid in dirtyids:
        try:
            GroupMembers.objects(gid=gid).delete()
        except OperationError:
            GroupMembers.objects(gid=gid).delete()

def _dirtyCyclesRemoveAll():
    #Remove dirty records in Cycles.
    cyclesids=[]
    for cycle in Cycles.objects():
        for sid in cycle.sids:
            cyclesids.append(sid)
    sessionids = Sessions.objects().distinct('sid')

    dirtyids = cyclesids - sessionids
    for sid in dirtyids:
        cycle = Cycles.objects(sids=sid).first()
        try:
            cycle.update(pull__sids=sid)
            cycle.reload()
            if not cycle.sids:
                cycle.delete()
        except OperationError:
            cycle.update(pull__sids=sid)
            cycle.reload()
            if not cycle.sids:
                cycle.delete()            

def dirtyDataRemoveAll():
    """
       Scheduled task to remove all the dirty data(file, case, session) from database
    """
    _dirtyGroupMemberRemoveAll()
    _dirtyCyclesRemoveAll()
    _dirtySessionRemoveAll()
    _dirtyCaseRemoveAll()
    _dirtyFileRemoveAll()