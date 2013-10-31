#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db import *
from filedealer import deleteFile

def sessionUpdateDomainSummary(sid, results):
    """
       Task func to update session domain count
    """
    print "Start updating the domain summary of session %d" %sid
    domaincount = Sessions.objects(sid=sid).first().domaincount
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
    try:
        Sessions.objects(sid=sid).update(set__domaincount=domaincount)
    except OperationError:
        Sessions.objects(sid=sid).update(set__domaincount=domaincount)

def sessionActiveSession(sid):
    """
       Task function to clear session endtime if it has been set.
    """
    print "Start activate session %d" %sid
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
    print "Start setting the endtime of session %d" %sid
    if not Cases.objects(sid=sid):
        endtime = Sessions.objects(sid=sid).first().starttime
    else:
        case = Cases.objects(sid=sid).order_by('-tid').first()
        endtime = case.endtime if case.endtime else case.starttime

    cache.clearCache(str('sid:' + str(sid) + ':snap'))
    cache.clearCache(str('sid:' + str(sid) + ':snaptime'))
    try:
        Sessions.objects(sid=sid).update(set__endtime=endtime)
    except OperationError:
        Sessions.objects(sid=sid).update(set__endtime=endtime)

def caseValidateEndtime():
    """
       Used to validate case endtime
    """
    # I dont think this is a reasonable function.
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

def sessionRemoveAll(sid):
    """
       Task to remove all the cases of a session and case log/snapshots 
    """
    print "Start remove session %d" %sid
    fid = []
    for case in Cases.objects(sid=sid, result='fail'):
        if case.log:
            fid.append(case.log)
        if case.expectshot:
            fid.append(case.expectshot)
        if case.snapshots:
            fid += case.snapshots
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
    #Remove dirty files.
    fileids, casefileids, avatarids = [], [], []
    for f in Files.objects():
        fileids.append(f.fileid)
    for case in Cases.objects(result='fail'):
        if case.log:
            casefileids.append(case.log)
        if case.expectshot:
            casefileids.append(case.expectshot)
        if case.snapshots:
            casefileids += case.snapshots
    for user in Users.objects():
        if user.avatar:
            avatarids.append(user.avatar)

    dirtyids = fileids - casefileids - avatarids
    deleteFile(dirtyids)

def _dirtyCaseRemoveAll():
    #Remove dirty cases
    casesids = Cases.objects().distinct('sid')
    sessionids = Sessions.objects().distinct('sid')

    dirtyids = casesids - sessionids

    for sid in dirtyids:
        try:
            Cases.objects(sid=sid).delete()
        except OperationError:
            Cases.objects(sid=sid).delete()

def _dirtySessionRemoveAll():
    #Remove dirty sessions.
    sessiongids = Sessions.objects().distinct('gid')
    groupids = Groups.objects().distinct('gid')

    dirtyids = sessiongids - groupids

    for gid in dirtyids:
        try:
            Sessions.objects(gid=gid).delete()
        except OperationError:
            Sessions.objects(gid=gid).delete()

def dirtyDataRemoveAll():
    """
       Scheduled task to remove all the dirty data(file, case, session, group) from database
    """
    _dirtyFileRemoveAll()
    _dirtyCaseRemoveAll()
    _dirtySessionRemoveAll()