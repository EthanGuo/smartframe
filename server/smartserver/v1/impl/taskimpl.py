#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db import *
from filedealer import deleteFile
from util import cache
import json, time

def sessionUpdateDomainSummary(sid, results):
    """
       Task func to update session domain count
    """
    print "Start updating the domain summary of session %s" %sid
    domaincount = Sessions.objects(sid=sid).first().domaincount
    if domaincount:
        domaincount = json.loads(domaincount)
    else:
        domaincount = {}
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
        if (time.time() - UserTokens.objects(uid=user.uid).first().expires) >= 0:
            user.delete()
    #If token has expired, remove it from database.
    for usertoken in UserTokens.objects():
        if (time.time() - usertoken.expires) >= 0:
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
    casefileids, avatarids = set(), set()
    fileids = set(Files.objects().distinct('fileid'))
    for case in Cases.objects(result='fail'):
        if case.log:
            casefileids.add(_getID(case.log))
        if case.expectshot:
            casefileids.add(_getID(case.expectshot))
        if case.snapshots:
            for snap in case.snapshots:
                casefileids.add(_getID(snap))
    for user in Users.objects():
        if user.avatar:
            avatarids.add(_getID(user.avatar))

    deleteFile((fileids - casefileids - avatarids))

def _dirtyCaseRemoveAll():
    #Remove dirty records in Cases
    casesids = set(Cases.objects().distinct('sid'))
    sessionids = set(Sessions.objects().distinct('sid'))

    for sid in casesids - sessionids:
        try:
            Cases.objects(sid=sid).delete()
        except OperationError:
            Cases.objects(sid=sid).delete()

def _dirtySessionRemoveAll():
    #Remove dirty records in Sessions.
    sessiongids = set(Sessions.objects().distinct('gid'))
    groupids = set(Groups.objects().distinct('gid'))

    for gid in sessiongids - groupids:
        try:
            Sessions.objects(gid=gid).delete()
        except OperationError:
            Sessions.objects(gid=gid).delete()

def _dirtyGroupMemberRemoveAll():
    #Remove dirty records in GroupMembers.

    membergids = set(GroupMembers.objects().distinct('gid'))
    groupids = set(Groups.objects().distinct('gid'))

    for gid in membergids - groupids:
        try:
            GroupMembers.objects(gid=gid).delete()
        except OperationError:
            GroupMembers.objects(gid=gid).delete()

def _dirtyCyclesRemoveAll():
    #Remove dirty records in Cycles.
    cyclesids = set()
    for cycle in Cycles.objects():
        cyclesids.update(cycle.sids)
    sessionids = set(Sessions.objects().distinct('sid'))

    for sid in cyclesids - sessionids:
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
    print "Start removing all the dirty files of server" 
    _dirtyGroupMemberRemoveAll()
    _dirtyCyclesRemoveAll()
    _dirtySessionRemoveAll()
    _dirtyCaseRemoveAll()
    _dirtyFileRemoveAll()