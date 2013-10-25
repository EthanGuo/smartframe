#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import resultWrapper, cache, redis_con
from mongoengine import OperationError
from datetime import datetime
from db import Sessions, Cycles, Users, Cases, GroupMembers
import json

def sessionCreate(data, gid, sid, uid):
    """
    params, data: {'planname':(string)value,'starttime':(string)value,
                   'deviceinfo':{'revision':(string)revision,'product':(string)product, 
                                 'width':(int)width, 'height':(int)height}}
    return, data: {}
    """
    #create a new session if save fail return exception
    sessionInst = Sessions().from_json(json.dumps({'gid': int(gid), 'sid': int(sid),'uid':int(uid),
                                      'planname':data['planname'],'starttime':data['starttime'],
                                      'deviceinfo':data['deviceinfo']}))
    if not data.get('deviceid'):
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
        if (data['cid'] == 0):
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
        if (data['cid'] == -1):
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
            Cycles.objects(cid=data['cid']).update(push__sids=sid)
            cid = Cycles.objects(sids=sid).first().cid
        except OperationError:
            return resultWrapper('error', {}, 'Add current session to cycle failed!')
        return resultWrapper('ok', {'cid': cid}, '')
    
    # Update endtime here.
    if 'endtime' in data:
        cache.clearCache(str('sid:' + str(sid) + ':snap'))
        cache.clearCache(str('sid:' + str(sid) + ':snaptime'))
        try:
            Sessions.objects(sid=sid).update(set__endtime=data['endtime'])
        except OperationError:
            return resultWrapper('error', {}, 'Update session endtime failed!')
        # send session heart to sessionwatcher and remove current sid from the watcher list.
        redis_con.publish("session:heartbeat", json.dumps({'clear': sid}))
        return resultWrapper('ok', {}, '')

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
                   'starttime':(datetime)starttime,'updatetime':updatetime,
                   'gid':(int)gid, 'sid':(int)sid, 
                   'deviceid':deviceid, summary':casecount,'deviceinfo':deviceinfo}
    """
    result = Sessions.objects(sid = int(sid)).first()
    if result:
        tester = Users.objects(uid =result.uid).first().username
        deviceinfo = result.deviceinfo.__dict__['_data'] if result.deviceinfo else ''
        casecount = result.casecount.__dict__['_data'] if result.casecount else ''
        data ={'planname':result.planname,'tester':tester,
               'deviceid':result.deviceid, 'deviceinfo':deviceinfo,
               'starttime':result.starttime,'updatetime':result.updatetime,
               'summary':casecount,'gid': gid, 'sid': sid}
        return resultWrapper('ok',data,'')
    else:
        return resultWrapper('error', {}, 'Invalid session ID!')

def sessionPollStatus(data, gid, sid):
    """
    params, data: {'tid': (int)value}
    return, data: {}
    """
    #return 'ok' means session has been updated already, 'error' means not yet.
    if Cases.objects(sid=int(sid), tid__gt=data['tid']):
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
        starttime = case.starttime.strftime("%Y-%m-%d %H:%M:%S") if case.starttime else ''
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
    totalamount = sess.first().casecount.totalnum if sess.first() else 0
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
        starttime = c.starttime.strftime("%Y-%m-%d %H:%M:%S") if c.starttime else ''
        result.append({'tid': c.tid, 'casename': c.casename, 
                       'starttime': starttime, 'result': c.result, 
                       'traceinfo': c.traceinfo, 'comments': comments})
    return resultWrapper('ok', {'cases': result, 'totalpage': totalpageamount}, '')
