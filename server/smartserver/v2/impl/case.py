#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import resultWrapper, cache, redis_con
from mongoengine import OperationError
from db import Cases
from filedealer import saveFile
from datetime import datetime
from ..config import TIME_FORMAT
from ..tasks import ws_update_session_domainsummary, ws_active_testsession
import session
import json

def caseresultCreate(data, sid):
    """
    params, data: {'tid':(int), 'casename':(string), 'starttime':(string)}
    return, data: {}
    """
    sid = int(sid)
    #create a new case if save failed return error
    caseInst = Cases().from_json(json.dumps({'sid': sid,'tid':data.get('tid'),'casename':data.get('casename'),'result':'running','starttime':data.get('starttime')}))
    try:
        caseInst.save()
    except OperationError:
        return resultWrapper('error',{},'Failed to create the testcase!')
    #Set session alive here, clear endtime in another way.
    ws_active_testsession.delay(sid)
    #publish heart beat to session watcher here.
    redis_con.publish("session:heartbeat", json.dumps({'sid': sid}))
    return resultWrapper('ok',{},'')

def handleSnapshots(snapshots):
    if not snapshots:
        return []
    else:
        result = []
        for snapshot in snapshots:
            fileid = saveFile(snapshot['image'], 'image/png', snapshot['imagename'])
            result.append(fileid)
        return result

def caseresultUpdate(data, sid):
    """
    params, data: {'tid':(int)/(list)tid, 'result':['Pass'/'Fail'/'Error'],'endtime':(string)endtime, 'traceinfo':(string)traceinfo, 'comments': (dict)comments}
    return, data: {}
    """
    #update case result or add case comments
    #If tid is list, do add case comments, or update case result.
    sid, domains = int(sid), []
    if isinstance(data.get('tid'), list):
        if data.get('comments'):
            try:
                result = data['comments']['caseresult']
                for tid in data['tid']:
                    case = Cases.objects(sid=sid, tid=tid).first()
                    orgcommentresult = case.comments.caseresult if case.comments else ''
                    Cases.objects(sid=sid, tid=tid).update(set__comments=data.get('comments'))
                    domains.append([tid, result.lower(), orgcommentresult])
            except OperationError:
                return resultWrapper('error', {}, 'Failed to update case comments!')
            ws_update_session_domainsummary.delay(sid, domains)
        else:
            return resultWrapper('error',{}, 'Comments can not be empty!')
    elif isinstance(data.get('tid'), int):
        case = Cases.objects(sid=sid, tid=data['tid']).first()
        orgresult = case.result
        orgcommentresult = case.comments.caseresult if case.comments else ''
        # Fetch all the images saved to memcache before then clear the cache.
        # If case failed, save all the images fetched from memcache to database
        if data.get('result').lower() == 'fail':
            snapshots = cache.getCache(str('sid:' + str(sid) + ':tid:' + str(data['tid']) + ':snaps'))
            snapshots = handleSnapshots(snapshots)
        else:
            snapshots = []
        try:
            Cases.objects(sid=sid, tid=data['tid']).update(set__result=data.get('result').lower(), 
                                                           set__endtime=data.get('endtime'), 
                                                           set__traceinfo=data.get('traceinfo',''), 
                                                           push_all__snapshots=snapshots)
        except OperationError:
            return resultWrapper('error', {}, 'update caseresult failed!')
        finally:
            cache.clearCache(str('sid:' + str(sid) + ':tid:' + str(data['tid']) + ':snaps'))
        session.sessionUpdateSummary(sid, [data['result'].lower(), orgresult])
        ws_update_session_domainsummary.delay(sid, [[data['tid'], data['result'].lower(), orgcommentresult]])
        ws_active_testsession.delay(sid)
        #publish heart beat to session watcher here.
        redis_con.publish("session:heartbeat", json.dumps({'sid': int(sid)}))
        return resultWrapper('ok', {},'')

def uploadPng(sid, tid, imagedata, stype):
    """
    params, data: {'sid':(string)sid, 'tid':(string)tid, 'imagedata':(Bytes)imagedata, 'stype':(string)(imagetype:imagename)}
    return, data: {}
    """
    #If the image uploaded is type:expect, save it to database, if type:current, save it to memcache
    snaps = cache.getCache(str('sid:' + sid + ':tid:' + tid + ':snaps'))
    if snaps is None:
        snaps = []
    values = stype.split(':')
    imagetype, imagename = values[0], values[1]
    if imagetype == 'expect':
        imageid = saveFile(imagedata, 'image/png', imagename)
        try:
            Cases.objects(sid=int(sid), tid=int(tid)).update(set__expectshot=imageid)
        except OperationError:
            return resultWrapper('error', {}, 'Save image to database failed!')
    elif imagetype == 'current':
        snaps.append({'imagename': imagename, 'image': imagedata})
        #Following two caches are used for screen monitor
        timenow = datetime.now().strftime(TIME_FORMAT)
        cache.setCache(str('sid:' + sid + ':snap'), imagedata)
        cache.setCache(str('sid:' + sid + ':snaptime'), timenow)
        #Cache history snapshots for a testcase
        cache.setCache(str('sid:' + sid + ':tid:' + tid + ':snaps'), snaps)

def uploadZip(sid, tid, logdata, xtype):
    """
    params, data: {'sid':(string)sid, 'tid':(string)tid, 'logdata':(bytes)logdata}
    return, data: {}
    """
    try:
        filename = 'log-caseid-%s.zip' %tid
        fileid = saveFile(logdata, 'application/zip', filename)
        Cases.objects(sid=int(sid), tid=int(tid)).update(set__log=fileid)
    except OperationError:
        return resultWrapper('error', {}, 'Save log to database failed!')
