#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper
from mongoengine import OperationError
from db import session,cycle,cases
import json

def sessionCreate(gid,sid,uid,data):
    """
    params, data: {'planname':(string)value,'starttime':(string)value,'deviceinfo':{'revision':(string)revision,'product':(string)product, 'width':(int)width, 'height':(int)height}}
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
        return resultWrapper('error',{},'shwo except when create the session') 
    return resultWrapper('ok',{},'') 


def sessionUpdate(gid,sid,uid,data):
    """
    params, data: {'cid':(int)cid,'endtime':(datetime)endtime,'status':(string)status}
    return, data: {}
    """
    #update session cid or endtime
    #if cid =0 is create a new cycle else change cycle 
    if 'cid' in data:
        if data['cid'] == 0:
            cycleInst = cycle().from_json(json.dumps({'gid':int(gid),'sid':int(sid)}))
            try:
                cycleInst.save()

            except OperationError :
                return resultWrapper('error',{},'shwo except when create the cycle!') 	
        else:
            try:
                cycle.objects(gid = gid,sid = sid).update(set__cid =data['cid'])
            except OperationError :
                return resultWrapper('error',{},'shwo except when update the cycleId!')
        return resultWrapper('ok',{},'')
    else:
    	pass


def sessionDelete(gid,sid,uid,data):
    """
    params, data: {}
    return, data: {}
    """
    try:
        session.objects(gid = gid,sid = sid).delete()
        cycle.objects(gid = gid, sid = sid).delete()
        # cases.objects(gid = gid)
    except OperationError :
        return resultWrapper('error',{},'show except when delete the session!')
    return resultWrapper('ok',{},'')


def sessionsummary(gid,sid,data):
    """
    params, data: {}
    return, data: {'planname':(string)planname,'tester':(string)tester,'endtime':(datetime)endtime,'cid':(int)cid,'updatetime':updatetime,'summary':summary, 'deviceinfo':deviceinfo}
    """
    try:
        result = session.objects(gid = gid,sid = sid).first()
    except OperationError :
    	return resultWrapper('error',{},'find session show except!')
    if result is None :
        return resultWrapper('error',{},'can not find this session!')
    else:
        try:
            userresult = user.objects(uid =result.uid).first()
        except OperationError:
            return resultWrapper('error',{},'show except when find user!')

        data ={'planname':result.planname,'tester':userresult.username,
               'deviceid':result.deviceid, 'deviceinfo':result.deviceinfo,
               'starttime':result.starttime,'endtime':result.endtime,
               'updatetime':result.updatetime,'count':result.count}

        return resultWrapper('ok',data,'')
