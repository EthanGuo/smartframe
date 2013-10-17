#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import resultWrapper, cache
from mongoengine import OperationError
from db import cases, CaseImage
from datetime import datetime
import types, json
import hashlib, uuid
#import io

def generateUniqueID():
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    return m.hexdigest()

def caseresultCreate(data, gid, sid):
    """
    params, data: {'tid':tid,'casename':casename,'starttime':starttime,}
    return, data: {}
    """
    #create a new case if save fail return exception
    caseInst = cases().from_json(json.dumps({'gid': int(gid), 'sid': int(sid),'tid':data['tid'],'casename':data['casename'],'result':'running','starttime':data['starttime']}))
    try:
        caseInst.save()
    except OperationError :
        return resultWrapper('error',{},'shwo except when save the test case') 
    return resultWrapper('ok',{},'') 


def caseresultUpdate(data, gid, sid):
    """
    params, data: {'tid':(int)/(list)tid, 'result':['Pass'/'Fail'/'Error'],'endtime':(string)endtime, 'traceinfo':(string)traceinfo, 'comments': (dict)comments}
    return, data: {}
    """
    #update case result or add case comments
    #If tids is list, do add case comments,else update case result.
    if type(data['tids']) is types.ListType:
        for tid in data['tids']:
            try:
                cases.objects(gid = gid,sid= sid, tid= tid).update(set__comments = data['comments'])
            except OperationError:
                return resultWrapper('error', {}, 'Add comments failed!')
    else:
        try:
            cases.objects(gid = gid,sid= sid, tid= data['tids']).update(set__result = data['result'].lower(),set__endtime = data['endtime'],set__traceinfo = data['traceinfo'])
        except OperationError:
                return resultWrapper('error', {}, 'update caseresult failed!')
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
    #imagedata = io.BufferedReader(io.BytesIO(imagedata))
    if imagetype == 'expect':
        imageid = generateUniqueID()
        image = CaseImage(imagename=imagename, imageid=imageid)
        image.image = imagedata
        try:
            cases.objects(sid=int(sid), tid=int(tid)).update(push__expectshot=image)
        except OperationError:
            return resultWrapper('error', {}, 'Save image to database failed!')
    elif imagetype == 'current':
        snaps.append({'imagename': imagename, 'image': imagedata})
        timenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cache.setCache(str('sid:' + sid + ':snap'), imagedata)
        cache.setCache(str('sid:' + sid + ':snaptime'), timenow)
        cache.setCache(str('sid:' + sid + ':tid:' + tid + ':snaps'), snaps)

def uploadZip(gid, sid, tid, logdata, xtype):
    """
    params, data: {'gid':(string)gid, 'sid':(string)sid, 'tid':(string)tid, 'logdata':(bytes)logdata}
    return, data: {}
    """
    #logdata = io.BufferedReader(io.BytesIO(logdata))
    try:
        cases.objects(sid=int(sid), tid=int(tid)).update(set__log=logdata)
    except:
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
    snaps = []
    case = cases.objects(sid=sid, tid=tid)
    if case:
        case = case.first()
        checksnaps = {'imagename': case.expectsnap.imagename, 'imageid': case.expectsnap.imageid}
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
    case = cases.objects(sid=sid, tid=tid)
    if case:
        case = case.first()
        logfile = case.log.read()
        return resultWrapper('ok', {'logfile': logfile}, '')
    else:
        return resultWrapper('error', {}, 'Invalid ID!')

