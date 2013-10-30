#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db import *

def sessionUpdateDomainSummary(sid, results):
    """
       Task func to update session domain count
    """
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
    users = Users.objects(active=False)
    for user in users:
        if (time.time() - UserTokens.objects(uid=user.uid).first().expires) <= 0:
            user.delete()
            user.reload()
    #If token has expired, remove it from database.
    for usertoken in UserTokens.objects():
        if (time.time() - usertoken.expires) <= 0:
            UserTokens.objects(token=usertoken.token).delete()