#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper, cache, redis_con, convertTime
from mongoengine import OperationError
from ..config import TIME_FORMAT
from db import Sessions, Cycles, Users, Cases, GroupMembers
from ..tasks import ws_update_session_domainsummary, ws_del_session
from taskimpl import sessionUpdateSummary
import json

def sessionCreate(data, gid, sid, uid):
    """
    params, data: {'planname':(string),'starttime':(string),'deviceinfo':
                      {'deviceid':(string),'revision':(string),'product':(string), 
                       'width':(string), 'height':(string)}}
    return, data: {}
    """
    #create a new session if save fail return exception
    starttime = convertTime(data.get('starttime'))
    sessionInst = Sessions().from_json(json.dumps({'gid': int(gid), 'sid': sid,'uid':int(uid),
                                      'planname':data.get('planname', 'test'),'starttime':starttime,
                                      'deviceinfo':data.get('deviceinfo'),
                                      'casecount': {'total': 0, 'pass': 0, 'fail': 0, 'error': 0}}))
    try:
        sessionInst.save()
    except OperationError :
        return resultWrapper('error',{},'Failed to create session!')
    #publish heart beat to session watcher here.
    redis_con.publish("session:heartbeat", json.dumps({'sid': sid})) 
    return resultWrapper('ok',{},'')

def sessionUpdate(data, gid, sid, uid):
    """
    params, data: {'endtime':(datetime)endtime}
    return, data: {}
    """
    #update session endtime
    gid = int(gid)
    if 'endtime' in data:
        #Clear the cached image for screen monitor
        cache.clearCache(str('sid:' + sid + ':snap'))
        cache.clearCache(str('sid:' + sid + ':snaptime'))
        endtime = convertTime(data.get('endtime'))
        try:
            Sessions.objects(sid=sid).only('endtime').update(set__endtime=endtime)
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
    #TODO: only group admin, group owner and session generator can do cycle setting?
    Cid = data.get('cid')
    if (Cid == 0):
        if Cycles.objects(sids=sid):
            return resultWrapper('error', {}, 'Please remove session from current cycle first!')
        else:
            cycleinst = Cycles().from_json(json.dumps({'gid': gid, 'sids': [sid]}))
            try:
                cycleinst.save()
            except OperationError:
                return resultWrapper('error', {}, 'Create new cycle failed!')
            return resultWrapper('ok', {'cid': cycleinst.cid}, '')

    # If cid = -1, remove current session from cycle it belongs.
    if (Cid == -1):
        cycle = Cycles.objects(sids=sid).first() 
        if not cycle:
            return resultWrapper('error', {}, 'This session does not belong to any cycle!')
        else:
            try:
                cycle.update(pull__sids=sid)
                cycle.reload()
                if not cycle.sids:
                    cycle.delete()
            except OperationError:
                return resultWrapper('error', {}, 'Remove session from current cycle failed!')
            return resultWrapper('ok', {}, '')

    # For other case, remove session from current session then add it to new cycle.
    if not Cycles.objects(cid=Cid):
        return resultWrapper('error', {}, 'Invalid Cycle ID!')
    cycle = Cycles.objects(sids=sid).first()
    if cycle:
        if cycle.cid == Cid:
            return resultWrapper('error', {}, 'Joined this cycle already!')
        try:
            cycle.update(pull__sids=sid)
            cycle.reload()
            if not cycle.sids:
                cycle.delete()
        except OperationError:
            return resultWrapper('error', {}, 'Remove session from current cycle failed!')
    try:
        cycle = Cycles.objects(cid=Cid).first()
        cycle.update(push__sids=sid)
        cycle.reload()
    except OperationError:
        return resultWrapper('error', {}, 'Add current session to cycle failed!')
    return resultWrapper('ok', {'cid': cycle.cid}, '')

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
    summarys, domains = [], []
    for testcase in ET.parse(data).getroot().iter('testcase'):
        caseId = testcase.attrib['order']
        casename = ''.join([testcase.attrib['component'],'.',testcase.attrib['id'].split('_')[0]])
        for resultInfo in testcase.iter('result_info'):
            starttime = convertTime(resultInfo.find('start').text)
            endtime = convertTime(resultInfo.find('end').text)
            result = resultInfo.find('actual_result').text.lower()
        try:
            caseInst = Cases().from_json(json.dumps({'sid': sid, 'tid': int(caseId),
                                                     'casename': casename,'result': result,
                                                     'starttime': starttime, 'endtime': endtime,}))
            caseInst.save()
            summarys.append([result, 'running'])
            domains.append([int(caseId), result, ''])
        except OperationError:
            return resultWrapper('error', {}, 'Create case failed!')
    #update session summary here.
    sessionUpdateSummary(sid, summarys)
    #Trigger task to update domain summary here.
    ws_update_session_domainsummary.delay(sid, domains)

def sessionDelete(data, gid, sid, uid):
    """
    params, data: {}
    return, data: {}
    """
    gid, uid = int(gid), int(uid)
    member = GroupMembers.objects(gid=gid, uid=uid).only('role').first()
    role = member.role if member else -1
    session = Sessions.objects(sid=sid, uid=uid).only('endtime').first()
    if session and role > 8 and session.endtime:
        try:
            session.delete()
            cycle = Cycles.objects(gid=gid, sids=sid).only('sids').first()
            if cycle:
                cycle.update(pull__sids=sid)
                cycle.reload()
                if not cycle.sids:
                    cycle.delete()
        except OperationError :
            return resultWrapper('error', {}, 'Failed to remove the session!')
        redis_con.publish('session:heartbeat', json.dumps({'clear': sid}))
        ws_del_session(sid)
        return resultWrapper('ok',{},'')
    return resultWrapper('error', {}, 'Permission denied or session is still alive!')

def sessionSummary(data, gid, sid):
    """
    params, data: {}
    return, data: {'planname':(string)planname,'tester':(string)tester,
                   'starttime':(datetime)starttime,'runtime':runtime,
                   'gid':(int)gid, 'sid':(int)sid, 
                   'deviceid':deviceid, summary':casecount,'deviceinfo':deviceinfo}
    """
    result = Sessions.objects(sid=sid).only('uid', 'deviceinfo', 'starttime', 'planname', 'runtime', 'casecount').first()
    if result:
        tester = Users.objects(uid=result.uid).first().username
        deviceinfo = result.deviceinfo.__dict__['_data'] if result.deviceinfo else ''
        starttime = result.starttime.strftime(TIME_FORMAT) if result.starttime else ''
        data ={'planname':result.planname,'tester':tester,
               'deviceinfo':deviceinfo,
               'starttime':starttime,
               'runtime':result.runtime,
               'summary':result.casecount,
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
    if Cases.objects(sid=sid, tid__gt=data.get('tid')).only('tid'):
        return resultWrapper('ok', {}, 'Session has been updated!')
    else:
        return resultWrapper('error', {}, 'Session has NOT been updated yet!')

def sessionGetLatestCases(data, gid, sid):
    """
    params, data: {'amount': (int)value}
    return, data: {'cases': [{'tid':(int)tid, 'casename':(string)name, 'expectshot': (dict),
                              'snapshots': (list(dict)), 'log': (dict),
                              'starttime':(string)time, 'result':(string)result, 
                              'traceinfo':(string)trace, 'comments':(dict)comments},...]}
    """
    #Fetch the first 'amount'(20 for example) cases and return them.
    amount = 20 if not data.get('amount') else int(data.get('amount'))
    result = []
    for case in Cases.objects(sid=sid).order_by('-tid')[:amount]:
        comments = case.comments.__dict__['_data'] if case.comments else ''
        starttime = case.starttime.strftime(TIME_FORMAT) if case.starttime else ''
        result.append({'tid': case.tid, 'casename': case.casename, 'log': case.log,
                       'expectshot': case.expectshot, 'snapshots': case.snapshots,
                       'starttime': starttime,'result': case.result, 
                       'traceinfo': case.traceinfo,'comments': comments})
    return resultWrapper('ok', {'cases': result}, '')

def sessionGetHistoryCases(data, gid, sid):
    """
    params, data: {'pagenumber': (int)value, 'pagesize': (int)value, 'casetype': (string)['total/pass/fail/error']}
    return, data: {'totalpage':(int)value, 
                   'cases': [{'tid':(int)tid, 'casename':(string)name,
                              'log':(dict), 'expectshot':(dict), 'snapshots':(list(dict)),
                              'starttime':(string)time, 'result':(string)result, 
                              'traceinfo':(string)trace, 'comments':(dict)comments},...]}
    """
    #Fetch the cases of page 'pagenumber', 'pagesize' and 'casetype' can not customized.
    sess = Sessions.objects(sid=sid).only('casecount')
    if not sess:
        return resultWrapper('error', {}, 'Invalid session ID!')
    #To calculate how many pages are there in this session, for frontend display purpose
    pagesize = 100 if not data.get('pagesize') else int(data.get('pagesize'))
    totalamount = sess.first().casecount['total']
    if (totalamount % pagesize != 0):
        totalpageamount = totalamount / pagesize + 1
    else:
        totalpageamount = totalamount / pagesize
    #To calculate the startpoint and endpoint of the cases to fetch.
    pagenumber = 1 if not data.get('pagenumber') else int(data.get('pagenumber'))
    casetype = data.get('casetype', 'total')
    startpoint = (pagenumber - 1) * pagesize
    endpoint = startpoint + pagesize
    if casetype == 'total':
        case = Cases.objects(sid=sid).order_by('-tid')[startpoint : endpoint]
    else:
        case = Cases.objects(sid=sid, result=casetype).order_by('-tid')[startpoint : endpoint]

    result = []
    for c in case:
        comments = c.comments.__dict__['_data'] if c.comments else ''
        starttime = c.starttime.strftime(TIME_FORMAT) if c.starttime else ''
        result.append({'tid': c.tid, 'casename': c.casename, 'log': c.log,
                       'expectshot': c.expectshot, 'snapshots': c.snapshots,
                       'starttime': starttime, 'result': c.result, 
                       'traceinfo': c.traceinfo, 'comments': comments})
    return resultWrapper('ok', {'cases': result, 'totalpage': totalpageamount}, '')