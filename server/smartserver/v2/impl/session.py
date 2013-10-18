#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper, cache, redis_con
from mongoengine import OperationError
from db import groups, session, cycle, user, cases
import json

def sessionCreate(data, gid, sid, uid):
    """
    params, data: {'planname':(string)value,'starttime':(string)value,
                   'deviceinfo':{'revision':(string)revision,'product':(string)product, 
                                 'width':(int)width, 'height':(int)height}}
    return, data: {}
    """
    #create a new session if save fail return exception
    sessionInst = session().from_json(json.dumps({'gid': int(gid), 'sid': int(sid),'uid':int(uid),
                                      'planname':data['planname'],'starttime':data['starttime'],
                                      'deviceinfo':data['deviceinfo']}))
    if data['deviceid'] is None:
        sessionInst.deviceid = 'N/A'
    else:
        sessionInst.deviceid = data['deviceid']
    try:
        sessionInst.save()
    except OperationError :
        return resultWrapper('error',{},'Failed to create session!') 
    return resultWrapper('ok',{},'') 

def sessionUpdate(data, gid, sid, uid):
    """
    params, data: {'cid':(int)cid,'endtime':(datetime)endtime,'status':(string)status}
    return, data: {}
    """
    #update session cid or endtime
    gid, sid = int(gid), int(sid)
    if 'cid' in data:
        # If cid = 0, create a new cycle and add sid to it.
        if (data['cid'] == 0) and cycle.objects(sids=sid):
            return resultWrapper('error', {}, 'Please remove session from current cycle first!')
        else:
            cycleinst = cycle().from_json(json.dumps({'gid': gid, 'sids': [sid]}))
            try:
                cycleinst.save()
                cid = cycle.objects(sids=sid).first().cid
            except OperationError:
                return resultWrapper('error', {}, 'Create new cycle failed!')
            return resultWrapper('ok', {'cid': cid}, '')
            # If cid = -1, remove current session from cycle it belongs.
        if (data['cid'] == -1) and not cycle.objects(sids=sid):
            return resultWrapper('error', {}, 'This session does not belong to any cycle!')
        else:
            try:
                cycle.objects(sids=sid).update(pull__sids=sid)
            except OperationError:
                return resultWrapper('error', {}, 'Remove session from current cycle failed!')
            return resultWrapper('ok', {}, '')
        # For other case, remove session from current session then add it to new cycle.
        if cycle.objects(sids=sid):
            try:
                cycle.objects(sids=sid).update(pull__sids=sid)
                cycle.objects(cid=data['cid']).update(push__sids=sid)
                cid = cycle.objects(sids=sid).first().cid
            except OperationError:
                return resultWrapper('error', {}, 'Change cycle failed!')
            return resultWrapper('ok', {'cid': cid}, '')
        else:
            try:
                cycle.objects(cid=data['cid']).update(push__sids=sid)
                cid = cycle.objects(sids=sid).first().cid
            except OperationError:
                return resultWrapper('error', {}, 'Add current session to cycle failed!')
            return resultWrapper('ok', {'cid': cid}, '')
    
    # Update endtime here.
    if 'endtime' in data:
        cache.clearCache(str('sid:' + str(sid) + ':snap'))
        cache.clearCache(str('sid:' + str(sid) + ':snaptime'))
        try:
            session.objects(sid=sid).update(set__endtime=data['endtime'])
        except OperationError:
            return resultWrapper('error', {}, 'Update session endtime failed!')
        return resultWrapper('ok', {}, '')
    # send session heart to sessionwatcher and remove current sid from the watcher list.
    redis_con.publish("session:heartbeat", json.dumps({'clear': sid}))

def sessionDelete(data, gid, sid, uid):
    """
    params, data: {}
    return, data: {}
    """
    gid, sid, uid = int(gid), int(sid), int(uid)
    for member in groups.objects(gid=gid).first().members:
        if member.uid == uid:
            role = member.role
    if session.objects(sid=sid, uid=uid) or (role > 8):
        try:
            session.objects(sid=sid).delete()
            if cycle.objects(gid=gid, sids=sid):
                cycle.objects(sids=sid).update(pull__sids=sid)
        except OperationError :
            return resultWrapper('error', {}, 'Failed to remove the session!')
        #Task to remove all the cases in this session.
        return resultWrapper('ok',{},'')

def sessionsummary(data, gid, sid):
    """
    params, data: {}
    return, data: {'planname':(string)planname,'tester':(string)tester,
                   'starttime':(datetime)starttime,'updatetime':updatetime,
                   'gid':(int)gid, 'sid':(int)sid, 
                   'deviceid':deviceid, summary':casecount,'deviceinfo':deviceinfo}
    """
    result = session.objects(sid = int(sid)).first()
    tester = user.objects(uid =result.uid).first().username
    data ={'planname':result.planname,'tester':tester,
           'deviceid':result.deviceid, 'deviceinfo':result.deviceinfo,
           'starttime':result.starttime,'updatetime':result.updatetime,
           'summary':result.casecount, 'gid': gid, 'sid': sid}
    return resultWrapper('ok',data,'')
