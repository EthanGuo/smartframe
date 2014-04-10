#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import resultWrapper, convertTime
from mongoengine import OperationError
from db import Cases, Sessions
from filedealer import saveFile
from datetime import datetime
from ..config import TIME_FORMAT
from ..tasks import ws_update_session_domainsummary, ws_active_testsession, ws_update_session_sessionsummary, ws_create_session_enddomainsummary, ws_update_session_enddomainsummary

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
    #ws_active_testsession.delay(sid)
    return resultWrapper('ok',{},'')

def __updateCaseComments(data, sid):
    endtag, domains, enddomains = False, [], []
    if data.get('comments'):
        result = data['comments']['caseresult']
        if not (result in ['fail', 'block', '']):
            return resultWrapper('error', {}, 'Invalid result!')
        session = Sessions.objects(sid=sid).only('endtid', 'enddomaincount').first()
        for tid in data['tid']:
            result = data['comments']['caseresult']
            case = Cases.objects(sid=sid, tid=tid).only('comments', 'result').first()
            if not (case.result.lower() in ['fail', 'error']):
                return resultWrapper('error', {}, "Can only add comments to fail/error cases!")
            if case.comments and case.comments.caseresult:
                orgcommentresult = case.comments.caseresult
            else:
                orgcommentresult = case.result
            if not result:
                result = case.result

            if data['comments']['endsession'] == 1:
                if data['comments']['caseresult'] != 'fail':
                    return resultWrapper('error', {}, 'Session should end at a failed case!')
                if len(data['tid']) == 1 and not session.endtid:
                    session.update(set__endtid=tid)
                    session.reload()
                    endtag = True
                    enddomains.append([tid, result.lower(), orgcommentresult])
                else:
                    return resultWrapper('error', {}, 'Session end can only be set to one case!')
            else: 
                if session.endtid == tid:
                    session.update(set__endtid=None, set__enddomaincount=None)
                    session.reload()
                elif session.endtid and session.endtid > tid:
                    enddomains.append([tid, result.lower(), orgcommentresult])

            domains.append([tid, result.lower(), orgcommentresult])
        if endtag:
            ws_create_session_enddomainsummary(sid, session.endtid)
        try:
            Cases.objects(sid=sid, tid__in=data['tid']).update(set__comments=data['comments'], multi=True)
        except OperationError:
            Cases.objects(sid=sid, tid__in=data['tid']).update(set__comments=data['comments'], multi=True)
        if session.endtid:
            ws_update_session_enddomainsummary.delay(sid, enddomains)
        ws_update_session_domainsummary.delay(sid, domains)
        return resultWrapper('ok', {}, 'Update successfully!')
    else:
        return resultWrapper('error',{}, 'Comments can not be empty!')

def __caseresultInsert(data, sid):
    """
    This method will be used to insert a case result into database directly for the realtime upload request from Intel.
    data: {'tid':(int), 'casename':(string), 'starttime':(string), 'result':['Pass'/'Fail'/'Error/BLOCK'],'endtime':(string)endtime, 'traceinfo':(string)traceinfo}
    """
    starttime = convertTime(data.get('starttime'))
    endtime = convertTime(data.get('time'))
    orgresult, orgcommentresult = 'running', ''
    caseInst = Cases(sid=sid, tid=data.get('tid'), casename=data.get('casename'), starttime=starttime, endtime=endtime, result=data.get('result').lower(), traceinfo=data.get('traceinfo', ''))
    try:
        caseInst.save()
    except OperationError:
        caseInst.save()
    ws_update_session_sessionsummary.delay(sid, [[data['result'].lower(), orgresult]])
    ws_update_session_domainsummary.delay(sid, [[data['tid'], data['result'].lower(), orgcommentresult]])
    #ws_active_testsession.delay(sid)
    return resultWrapper('ok', {}, '')

def __updateCaseResult(data, sid):
    case = Cases.objects(sid=sid, tid=data['tid']).only('result', 'comments').first()
    if not case:
        return __caseresultInsert(data, sid)
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
    #ws_active_testsession.delay(sid)
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
    #If the image uploaded is type:expect, save it to expectshot, if type:current, save it to snapshots
    values = stype.split(':')
    imagetype, imagename = values[0], values[1]
    imageurl = saveFile(imagedata, 'image/png', imagename)
    snapfile = {'filename': imagename, 'url': imageurl}
    if imagetype == "expect":
        Cases.objects(sid=sid, tid=int(tid)).only('tid').update(set__expectshot={'filename': imagename, 'url': imageurl})
    elif imagetype == "current":
        Cases.objects(sid=sid, tid=int(tid)).only('tid').update(push__snapshots={'filename': imagename, 'url': imageurl})
    else:
        return resultWrapper('error', {}, 'Invalid image type value:%s!' % stype)
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
