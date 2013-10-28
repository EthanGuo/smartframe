#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper, cache, redis_con
from mongoengine import OperationError
from ..config import TIME_FORMAT
from db import Sessions, Cycles, Users, Cases, GroupMembers
import json

def sessionCreate(data, gid, sid, uid):
    """
    params, data: {'planname':(string),'starttime':(string),'deviceinfo':
                      {'deviceid':(string),'revision':(string),'product':(string), 
                       'width':(int), 'height':(int)}}
    return, data: {}
    """
    #create a new session if save fail return exception
    sessionInst = Sessions().from_json(json.dumps({'gid': int(gid), 'sid': int(sid),'uid':int(uid),
                                      'planname':data.get('planname', 'test'),'starttime':data.get('starttime'),
                                      'deviceinfo':data.get('deviceinfo'),
                                      'casecount': {'totalnum': 0, 'passnum': 0, 'failnum': 0, 'errornum': 0}}))
    try:
        sessionInst.save()
    except OperationError :
        return resultWrapper('error',{},'Failed to create session!')
    #publish heart beat to session watcher here.
    redis_con.publish("session:heartbeat", json.dumps({'sid': int(sid)})) 
    return resultWrapper('ok',{},'')

def sessionUpdate(data, gid, sid, uid):
    """
    params, data: {'endtime':(datetime)endtime}
    return, data: {}
    """
    #update session endtime
    gid, sid = int(gid), int(sid)
    if 'endtime' in data:
        #Clear the cached image for screen monitor
        cache.clearCache(str('sid:' + str(sid) + ':snap'))
        cache.clearCache(str('sid:' + str(sid) + ':snaptime'))
        try:
            Sessions.objects(sid=sid).update(set__endtime=data.get('endtime'))
        except OperationError:
            return resultWrapper('error', {}, 'Update session endtime failed!')
        # send session heart to sessionwatcher and remove current sid from the watcher list.
        redis_con.publish("session:heartbeat", json.dumps({'clear': sid}))
        return resultWrapper('ok', {}, '')

def sessionCycle(data, gid, sid, uid):
    """
    params, data: {'cid':(int)cid}
    return, data: {}
    """
    # If cid = 0, create a new cycle and add sid to it.
    Cid = data.get('cid')
    if (Cid == 0):
        if Cycles.objects(sids=sid):
            return resultWrapper('error', {}, 'Please remove session from current cycle first!')
        else:
            cycleinst = Cycles().from_json(json.dumps({'gid': gid, 'sids': [sid]}))
            try:
                cycleinst.save()
                cid = Cycles.objects(sids=sid).first().cid
            except OperationError:
                return resultWrapper('error', {}, 'Create new cycle failed!')
            return resultWrapper('ok', {'cid': cid}, '')

    # If cid = -1, remove current session from cycle it belongs.
    if (Cid == -1):
        if not Cycles.objects(sids=sid):
            return resultWrapper('error', {}, 'This session does not belong to any cycle!')
        else:
            try:
                Cycles.objects(sids=sid).update(pull__sids=sid)
            except OperationError:
                return resultWrapper('error', {}, 'Remove session from current cycle failed!')
            return resultWrapper('ok', {}, '')

    # For other case, remove session from current session then add it to new cycle.
    if Cycles.objects(sids=sid):
        try:
            Cycles.objects(sids=sid).update(pull__sids=sid)
        except OperationError:
            return resultWrapper('error', {}, 'Remove session from current cycle failed!')
    try:
        Cycles.objects(cid=Cid).update(push__sids=sid)
        cid = Cycles.objects(sids=sid).first().cid
    except OperationError:
        return resultWrapper('error', {}, 'Add current session to cycle failed!')
    return resultWrapper('ok', {'cid': cid}, '')

def sessionUploadXML(data, gid, sid):
    """
    params, data: stream data of xml uploaded
    return, data: {}
    """    
    try:
        import xml.etree.cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET
    #Parse the xml file to get case result data then save into database one by one.
    for testcase in ET.parse(data).getroot().iter('testcase'):
        caseId = testcase.attrib['order']
        casename = ''.join([testcase.attrib['component'],'.',testcase.attrib['id'].split('_')[0]])
        for resultInfo in testcase.iter('result_info'):
            starttime = resultInfo.find('start').text
            endtime = resultInfo.find('end').text
            result = resultInfo.find('actual_result').text.lower()
        try:
            caseInst = Cases().from_json(json.dumps({'sid': int(sid), 'tid': int(caseId),
                                                     'casename': casename,'result': result,
                                                     'starttime': starttime, 'endtime': endtime,}))
            caseInst.save()
        except OperationError:
            return resultWrapper('error', {}, 'Create case failed!')
    #TODO: update session summary here.

def sessionDelete(data, gid, sid, uid):
    """
    params, data: {}
    return, data: {}
    """
    gid, sid, uid = int(gid), int(sid), int(uid)
    member = GroupMembers.objects(gid=gid, uid=uid).first()
    role = member.role if member else -1
    if Sessions.objects(sid=sid, uid=uid) or (role > 8):
        try:
            Sessions.objects(sid=sid).delete()
            if Cycles.objects(gid=gid, sids=sid):
                Cycles.objects(sids=sid).update(pull__sids=sid)
        except OperationError :
            return resultWrapper('error', {}, 'Failed to remove the session!')
        #Task to remove all the cases in this session.
        return resultWrapper('ok',{},'')
    return resultWrapper('error', {}, 'Permission denied!')

def sessionSummary(data, gid, sid):
    """
    params, data: {}
    return, data: {'planname':(string)planname,'tester':(string)tester,
                   'starttime':(datetime)starttime,'runtime':runtime,
                   'gid':(int)gid, 'sid':(int)sid, 
                   'deviceid':deviceid, summary':casecount,'deviceinfo':deviceinfo}
    """
    result = Sessions.objects(sid=int(sid)).first()
    if result:
        tester = Users.objects(uid=result.uid).first().username
        deviceinfo = result.deviceinfo.__dict__['_data'] if result.deviceinfo else ''
        data ={'planname':result.planname,'tester':tester,
               'deviceinfo':deviceinfo,
               'starttime':result.starttime.strftime(TIME_FORMAT),
               'runtime':result.runtime,
               'summary':result.casecount.__dict__['_data'],
               'gid': gid, 'sid': sid}
        return resultWrapper('ok',data,'')
    else:
        return resultWrapper('error', {}, 'Invalid session ID!')

def sessionPollStatus(data, gid, sid):
    """
    params, data: {'tid': (int)value}
    return, data: {}
    """
    #return 'ok' means session has been updated already, 'error' means not yet.
    if Cases.objects(sid=int(sid), tid__gt=data.get('tid')):
        return resultWrapper('ok', {}, 'Session has been updated!')
    else:
        return resultWrapper('error', {}, 'Session has NOT been updated yet!')

def sessionGetLatestCases(data, gid, sid):
    """
    params, data: {'amount': (int)value}
    return, data: {'cases': [{'tid':(int)tid, 'casename':(string)name, 
                              'starttime':(string)time, 'result':(string)result, 
                              'traceinfo':(string)trace, 'comments':(dict)comments},...]}
    """
    #Fetch the first 'amount'(20 for example) cases and return them.
    amount = data.get('amount', 20)
    result = []
    for case in Cases.objects(sid=int(sid)).order_by('-tid')[:amount]:
        comments = case.comments.__dict__['_data'] if case.comments else ''
        starttime = case.starttime.strftime(TIME_FORMAT) if case.starttime else ''
        result.append({'tid': case.tid, 'casename': case.casename, 
                       'starttime': starttime,'result': case.result, 
                       'traceinfo': case.traceinfo,'comments': comments})
    return resultWrapper('ok', {'cases': result}, '')

def sessionGetHistoryCases(data, gid, sid):
    """
    params, data: {'pagenumber': (int)value, 'pagesize': (int)value, 'casetype': (string)['total/pass/fail/error']}
    return, data: {'totalpage':(int)value, 
                   'cases': [{'tid':(int)tid, 'casename':(string)name, 
                              'starttime':(string)time, 'result':(string)result, 
                              'traceinfo':(string)trace, 'comments':(dict)comments},...]}
    """
    #Fetch the cases of page 'pagenumber', 'pagesize' and 'casetype' can not customized.
    sess = Sessions.objects(sid=int(sid))
    if not sess:
        return resultWrapper('error', {}, 'Invalid session ID!')
    #To calculate how many pages are there in this session, for frontend display purpose
    pagesize = data.get('pagesize', 100)
    totalamount = sess.first().casecount.totalnum
    if (totalamount % pagesize != 0):
        totalpageamount = totalamount / pagesize + 1
    else:
        totalpageamount = totalamount / pagesize
    #To calculate the startpoint and endpoint of the cases to fetch.
    pagenumber = data.get('pagenumber', 1)
    casetype = data.get('casetype', 'total')
    startpoint = (pagenumber - 1) * pagesize
    endpoint = startpoint + pagesize
    if casetype == 'total':
        case = Cases.objects(sid=int(sid)).order_by('-tid')[startpoint : endpoint]
    else:
        case = Cases.objects(sid=int(sid), result=casetype).order_by('-tid')[startpoint : endpoint]

    result = []
    for c in case:
        comments = c.comments.__dict__['_data'] if c.comments else ''
        starttime = c.starttime.strftime(TIME_FORMAT) if c.starttime else ''
        result.append({'tid': c.tid, 'casename': c.casename, 
                       'starttime': starttime, 'result': c.result, 
                       'traceinfo': c.traceinfo, 'comments': comments})
    return resultWrapper('ok', {'cases': result, 'totalpage': totalpageamount}, '')



def sessionUpdateSummary(sid, tid, result):
    """
       Task func to update session casecount summary and domain summary
    """
    # Update casecount here.
    try:
        #Use signal to update total, need optimise
        Sessions.objects(sid=sid).update(inc__casecount__totalnum=1)
        if result == 'pass':
            Sessions.objects(sid=sid).update(inc__casecount__passnum=1)
        elif result == 'fail':
            Sessions.objects(sid=sid).update(inc__casecount__failnum=1)
        elif result == 'error':
            Sessions.objects(sid=sid).update(inc__casecount__errornum=1)
        #Update session runtime here.
    except OperationError:
        #Use signal to update total, need optimise
        Sessions.objects(sid=sid).update(inc__casecount__totalnum=1)
        if result == 'pass':
            Sessions.objects(sid=sid).update(inc__casecount__passnum=1)
        elif result == 'fail':
            Sessions.objects(sid=sid).update(inc__casecount__failnum=1)
        elif result == 'error':
            Sessions.objects(sid=sid).update(inc__casecount__errornum=1)
        #Update session runtime here.

    #Update domaincount here.
    casename = Cases.objects(sid=sid, tid=tid).first().casename
    domain = casename.strip().split('.')[0]
    domaincount = Sessions.objects(sid=sid).first().domaincount
    if domain in domaincount.keys():
        domaincount[domain]['total'] += 1
        domaincount[domain][result] += 1
    else:
        domaincount[domain] = {'total': 1, 'pass': 0, 'fail': 0, 'error': 0}
        domaincount[domain][result] += 1
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