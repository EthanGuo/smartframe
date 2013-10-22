#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import resultWrapper, cache, redis_con, generateUniqueID
from mongoengine import OperationError
from db import cases, CaseImage, Log
from datetime import datetime
import json

def caseresultCreate(data, gid, sid):
    """
    params, data: {'tid':tid,'casename':casename,'starttime':starttime}
    return, data: {}
    """
    #create a new case if save fail return exception
    caseInst = cases().from_json(json.dumps({'gid': int(gid), 'sid': int(sid),'tid':data['tid'],'casename':data['casename'],'result':'running','starttime':data['starttime']}))
    try:
        caseInst.save()
    except OperationError :
        return resultWrapper('error',{},'Failed to create the testcase!')
    #TODO: Set session alive here, clear endtime in another way. 
    return resultWrapper('ok',{},'') 

def handleSnapshots(snapshots):
    if not snapshots:
        return []
    else:
        result = []
        for snapshot in snapshots:
            tmp = CaseImage(imageid=snapshot['imageid'], imagename=snapshot['imagename'])
            tmp.image.new_new()
            tmp.image.write(snapshot['image'])
            tmp.image.close()
            result.append(tmp)
        return result

def caseresultUpdate(data, gid, sid):
    """
    params, data: {'tid':(int)/(list)tid, 'result':['Pass'/'Fail'/'Error'],'endtime':(string)endtime, 'traceinfo':(string)traceinfo, 'comments': (dict)comments}
    return, data: {}
    """
    #update case result or add case comments
    #If tid is list, do add case comments,else update case result.
    gid, sid = int(gid), int(sid)
    if isinstance(data['tid'], list):
        try:
            for tid in data['tid']:
                cases.objects(gid=gid, sid=sid, tid=tid).update(set__comments=data['comments'])
        except OperationError:
            return resultWrapper('error', {}, 'Failed to update case comments!')
    else:
        # Fetch all the images saved to memcache before then clear the cache.
        # If case failed, save all the images fetched from memcache to database
        if data['result'].lower() == 'fail':
            snapshots = cache.getCache(str('sid:' + str(sid) + ':tid:' + str(data['tid']) + ':snaps'))
            snapshots = handleSnapshots(snapshots)
        else:
            snapshots = []
        try:
            cases.objects(gid=gid, sid=sid, tid=data['tid']).update(set__result=data['result'].lower(), 
                                                                    set__endtime=data['endtime'], 
                                                                    set__traceinfo=data['traceinfo'], 
                                                                    push_all__snapshots=snapshots)
        except OperationError:
            return resultWrapper('error', {}, 'update caseresult failed!')
        finally:
            cache.clearCache(str('sid:' + str(sid) + ':tid:' + str(data['tid']) + ':snaps'))
    #TODO: trigger the task to update session summary here.
    #TODO: Set session alive here, clear endtime in another way.
    #publish heart beat to session watcher here.
    redis_con.publish("session:heartbeat", json.dumps({'sid': sid}))
    return resultWrapper('ok', {},'')

def uploadPng(gid, sid, tid, imagedata, stype):
    """
    params, data: {'gid':(string)gid, 'sid':(string)sid, 'tid':(string)tid, 'imagedata':(Bytes)imagedata, 'stype':(string)(imagetype:imagename)}
    return, data: {}
    """
    #If the image uploaded is type:expect, save it to database, if type:current, save it to memcache
    snaps = cache.getCache(str('sid:' + sid + ':tid:' + tid + ':snaps'))
    if snaps is None:
        snaps = []
    values = stype.split(':')
    imagetype, imagename = values[0], values[1]
    if imagetype == 'expect':
        imageid = generateUniqueID()
        image = CaseImage(imagename=imagename, imageid=imageid)
        image.image.new_file()
        image.image.write(imagedata)
        image.image.close()
        try:
            cases.objects(sid=int(sid), tid=int(tid)).update(set__expectshot=image)
        except OperationError:
            return resultWrapper('error', {}, 'Save image to database failed!')
    elif imagetype == 'current':
        imageid = generateUniqueID()
        snaps.append({'imagename': imagename, 'image': imagedata, 'imageid': imageid})
        timenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #Following two caches are used for screen monitor
        cache.setCache(str('sid:' + sid + ':snap'), imagedata)
        cache.setCache(str('sid:' + sid + ':snaptime'), timenow)
        #Cache history snapshots for a testcase
        cache.setCache(str('sid:' + sid + ':tid:' + tid + ':snaps'), snaps)

def uploadZip(gid, sid, tid, logdata, xtype):
    """
    params, data: {'gid':(string)gid, 'sid':(string)sid, 'tid':(string)tid, 'logdata':(bytes)logdata}
    return, data: {}
    """
    try:
        log = Log()
        log.log.new_file()
        log.log.write(logdata)
        log.log.close()
        cases.objects(sid=int(sid), tid=int(tid)).update(set__log=log)
    except OperationError:
        return resultWrapper('error', {}, 'Save log to database failed!')

def testcaseGetSnapData(imageid):
    """
    params, data: {'imageid':(string)imageid}
    return, data: {'imagedata':(bytes)imagedata}
    """
    #If imageid is valid, return imagedata, or return error
    case = cases.objects(snapshots__imageid=imageid)
    if case:
        for image in case.first().snapshots:
            if image.imageid == imageid:
                return resultWrapper('ok', {'imagedata': image.image.read()}, '')
    else:
        case = cases.objects(expectshot__imageid=imageid)
        if case:
            return resultWrapper('ok', {'imagedata': case.first().expectshot.image.read()}, '')
        else:
            return resultWrapper('error', {}, 'Invalid ID!')

def testcaseGetSnapshots(gid, sid, tid):
    """
    params, data: {'gid':gid, 'sid':sid, 'tid':tid}
    return, data: {'snaps': [{'imagename':imagename, 'imageid': imageid}, {...}], 'checksnaps': {'imagename':imagename, 'imageid': imageid}}
    """
    #If ids are valid, return all the images, or return error
    snaps, checksnaps = [], {}
    case = cases.objects(sid=int(sid), tid=int(tid)).first()
    if case and (case.result == 'fail'):
        if case.expectshot:
            checksnaps.update({'imagename': case.expectshot.imagename, 'imageid': case.expectshot.imageid})
        for snap in case.snapshots:
            snaps.append({'imagename': snap.imagename, 'imageid': snap.imageid})
        return resultWrapper('ok', {'snaps': snaps, 'checksnaps': checksnaps}, '')
    else:
        return resultWrapper('error', {}, 'Invalid ID!')

def testcaseGetLog(gid, sid, tid):
    """
    params, data: {'gid':gid, 'sid':sid, 'tid':tid}
    return, data: {'logfile': logfile}
    """
    #If the IDs requested are valid, return logfile, or return error.
    case = cases.objects(sid=int(sid), tid=int(tid)).first()
    if case and (case.result == 'fail'):
        logfile = case.log.log.read()
        return resultWrapper('ok', {'logfile': logfile}, '')
    else:
        return resultWrapper('error', {}, 'Invalid ID!')

