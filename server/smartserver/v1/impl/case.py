#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import resultWrapper, cache, convertTime
from mongoengine import OperationError
from db import Cases, Sessions
from filedealer import saveFile
from datetime import datetime
from ..config import TIME_FORMAT
from ..tasks import ws_update_session_domainsummary, ws_active_testsession, ws_update_session_sessionsummary

def caseresultCreate(data, sid):
    """
    params, data: {'tid':(int), 'casename':(string), 'starttime':(string)}
    return, data: {}
    """
    #create a new case if save failed return error
    starttime = convertTime(data.get('starttime'))
    caseInst = Cases(sid=sid, tid=data.get('tid'), casename=data.get('casename'), result='running', starttime=starttime)
    try:
        caseInst.save()
    except OperationError:
        caseInst.save()
    #Set session alive here, clear endtime in another way.
    ws_active_testsession.delay(sid)
    return resultWrapper('ok',{},'')

def __updateCaseComments(data, sid):
    domains = []
    if data.get('comments'):
        result = data['comments']['caseresult']
        if not (result in ['fail', 'block', '']):
            return resultWrapper('error', {}, 'Invalid result!')
        session = Sessions.objects(sid=sid).only('endtid', 'enddomaincount').first()
        for tid in data['tid']:
            case = Cases.objects(sid=sid, tid=tid).only('comments', 'result').first()
            if not (case.result.lower() in ['fail', 'error']):
                return resultWrapper('error', {}, "Can only add comments to fail/error cases!")
            if data['comments']['endsession'] == 1:
                if len(data['tid']) == 1:
                    session.update(set__endtid=tid)
                    session.reload()
                else:
                    return resultWrapper('error', {}, 'Session end can only be set to one case!')
            elif session.endtid == tid:
                session.update(set__endtid=None, set__enddomaincount=None)
                session.reload()
            if case.comments and case.comments.caseresult:
                orgcommentresult = case.comments.caseresult
            else:
                orgcommentresult = case.result
            if not result:
                result = case.result
            domains.append([tid, result.lower(), orgcommentresult])
        try:
            Cases.objects(sid=sid, tid__in=data['tid']).update(set__comments=data['comments'], multi=True)
        except OperationError:
            Cases.objects(sid=sid, tid__in=data['tid']).update(set__comments=data['comments'], multi=True)
        ws_update_session_domainsummary.delay(sid, domains)
        return resultWrapper('ok', {}, 'Update successfully!')
    else:
        return resultWrapper('error',{}, 'Comments can not be empty!')

def __updateCaseResult(data, sid):
    case = Cases.objects(sid=sid, tid=data['tid']).only('result', 'comments').first()
    if not case:
        return resultWrapper('error', {}, 'Invalid case ID!')
    orgresult = case.result
    if case.comments and case.comments.caseresult:
        orgcommentresult = case.comments.caseresult
        case.update(set__comments={})
        case.reload()
    else:
        orgcommentresult = ''

    endtime = convertTime(data.get('time'))
    try:
        case.update(set__result=data.get('result').lower(), 
                    set__endtime=endtime, 
                    set__traceinfo=data.get('traceinfo',''))
        case.reload()
    except OperationError:
        case.update(set__result=data.get('result').lower(), 
                    set__endtime=endtime, 
                    set__traceinfo=data.get('traceinfo',''))
        case.reload()
    ws_update_session_sessionsummary.delay(sid, [[data['result'].lower(), orgresult]])
    ws_update_session_domainsummary.delay(sid, [[data['tid'], data['result'].lower(), orgcommentresult]])
    ws_active_testsession.delay(sid)
    return resultWrapper('ok', {},'')

def caseresultUpdate(data, sid):
    """
    params, data: {'tid':(int)/(list)tid, 'result':['Pass'/'Fail'/'Error'],'endtime':(string)endtime, 'traceinfo':(string)traceinfo, 'comments': (dict)comments}
    return, data: {}
    """
    #update case result or add case comments
    #If tid is list, do add case comments, or update case result.
    if isinstance(data.get('tid'), list):
        return __updateCaseComments(data, sid)
    elif isinstance(data.get('tid'), int):
        return __updateCaseResult(data, sid)

def uploadPng(sid, tid, imagedata, stype):
    """
    params, data: {'sid':(string)sid, 'tid':(string)tid, 'imagedata':(Bytes)imagedata, 'stype':(string)(imagetype:imagename)}
    return, data: {}
    """
    #If the image uploaded is type:expect, save it to database, if type:current, save it to memcache
    snaps = cache.getCache(str('sid:' + sid + ':tid:' + tid + ':snaps'))
    if not snaps:
        snaps = []
    values = stype.split(':')
    imagetype, imagename = values[0], values[1]
    imageurl = saveFile(imagedata, 'image/png', imagename)
    imagedata.seek(0)
    if imagetype == 'expect':
        #bond both snapshots and expectshots with case here.
        snapshots = cache.getCache(str('sid:' + sid + ':tid:' + str(tid) + ':snaps'))
        if not snapshots:
            snapshots = []
        try:
            Cases.objects(sid=sid, tid=int(tid)).only('tid').update(set__expectshot={'filename': imagename, 'url': imageurl}, push_all__snapshots=snapshots)
        except OperationError:
            Cases.objects(sid=sid, tid=int(tid)).only('tid').update(set__expectshot={'filename': imagename, 'url': imageurl}, push_all__snapshots=snapshots)
        finally:
            cache.clearCache(str('sid:' + sid + ':tid:' + str(tid) + ':snaps'))
    elif imagetype == 'current':
        snaps.append({'filename': imagename, 'url': imageurl})
        #Following two caches are used for screen monitor
        timenow = datetime.now().strftime(TIME_FORMAT)
        cache.setCache(str('sid:' + sid + ':snap'), imagedata.read())
        cache.setCache(str('sid:' + sid + ':snaptime'), timenow)
        #Cache history snapshots for a testcase
        cache.setCache(str('sid:' + sid + ':tid:' + tid + ':snaps'), snaps)
    return resultWrapper('ok', {'fileid': imageurl}, '')

def uploadZip(sid, tid, logdata, xtype):
    """
    params, data: {'sid':(string)sid, 'tid':(string)tid, 'logdata':(bytes)logdata}
    return, data: {}
    """
    filename = 'log-caseid-%s.zip' %tid
    fileurl = saveFile(logdata, 'application/zip', filename)
    try:
        Cases.objects(sid=sid, tid=int(tid)).only('tid').update(set__log={'filename': filename, 'url': fileurl})
    except OperationError:
        Cases.objects(sid=sid, tid=int(tid)).only('tid').update(set__log={'filename': filename, 'url': fileurl})
    return resultWrapper('ok', {'fileid': fileurl}, '')
