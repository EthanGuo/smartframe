#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent.pywsgi import WSGIServer
from bottle import request, Bottle, response
from plugins import ContentTypePlugin, DataFormatPlugin, LoginPlugin
from mapping import *

appweb = Bottle()

contenttype_plugin = ContentTypePlugin()
appweb.install(contenttype_plugin)

dataformat_plugin = DataFormatPlugin()
appweb.install(dataformat_plugin)

login_plugin = LoginPlugin(getuserid=getUserId,
                           request_token_param="token",
                           login=True)  # login is required by default
appweb.install(login_plugin)

@appweb.route('/accountbasic', method='POST', content_type='application/json', data_format=['subc', 'data'], login=False)
def doAccount():
    """
    URL:/accountbasic
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ---------------------------------------------------------------------------------------
    |support|subc           |data
    |       |register       |{'username':(string), 'password':(string), 'appid':(string),
    |       |               | 'info':{'email':(string), 'telephone':(string), 'company':(string)}, 'baseurl': (string)}
    |       |retrievepswd   |{'email':(string), 'baseurl': (string)}
    |       |login          |{'appid':(string), 'username':(string), 'password':(string)}
    ---------------------------------------------------------------------------------------
    """
    return accountBasic(request.json)

@appweb.route('/account', method='POST',content_type=['application/json','multipart/form-data'], data_format=['subc', 'data'])
def doAccountPOST(uid):
    """
    URL:/account
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc          |data
    |       |changepswd    |{'oldpassword':(string), 'newpassword':(string)}
    |       |update        |{'appid': (string), 'username':(string), 'telephone':(string), 'company':(string)}
    |       |invite        |{'email':(string)target email, 'username':(string)target name, 'baseurl': (string)}
    |       |logout        |{}
    -----------------------------------------------------------------------------------------
    """
    if 'multipart/form-data' in request.content_type:
        data = {'subc': 'update'}
        data['data'] = {'file': request.files.get('data')}
    else:
        data = request.json
    return accountPOST(data, uid)

@appweb.route('/account', method='GET')
def doAccountGET(uid):
    """
    URL:/account
    TYPE:http/GET
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc          |return data 
    |       |accountlist   |{'count':(int), 'users':[{'uid':(string),'username':(string)},...]}}
    |       |accountinfo   |{'username':(string),'info':{'email':(string), 'telephone':(string), 'company':(string)}}
    |       |groups        |{'groups':[{'gid':(int),'groupname':(string), 'allsession': (int)count, 'livesession': (int)count},...]}
    |       |sessions      |{'sessions': [{'sid':(int), 'gid':(int), 'groupname':(string)},...]}
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc')}
    return accountGet(data, uid)

@appweb.route('/group', method='POST',content_type='application/json', data_format=['subc', 'data'])
def doGroup(uid):
    """
    URL:/group
    TYPE:http/POST
    @data type:JSON
    @param: {'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc          |data 
    |       |create        |{'groupname':(string), 'info':(string)}
    -----------------------------------------------------------------------------------------
    """
    return groupBasic(request.json, uid)

@appweb.route('/group/<gid>', method='POST', content_type='application/json', data_format=['subc', 'data'])
def doGroupPOST(gid, uid):
    """
    URL:/group/<gid>
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc          |data 
    |       |delete        |{}
    |       |setmember     |{'members':[{'uid':(int),'role':(int)roleId}]}
    |       |delmember     |{'members':[{'uid':(int),'role':(int)roleId}]}
    -----------------------------------------------------------------------------------------
    """
    return groupPOST(request.json, gid, uid)

@appweb.route('/group/<gid>', method='GET')
def doGroupGET(gid, uid):
    """
    URL:/group/<gid>
    TYPE:http/GET
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc        |return data 
    |       |members     |{'members':[{'uid':(int), 'username':(string), 'role':(int), 'info':(dict)},...]   
    |       |sessions    |{'sessions': [{'gid':(int), 'product':(string), 'revision':(string), 
    |       |            |               'deviceid':(string), 'starttime':(string), 'endtime':(string),
    |       |            |               'runtime':(int), 'tester':(string)name},...]}
    |       |cycles      |{'cycles': [{'cid':(int), 'devicecount':(int), 'livecount':(int),
    |       |            |             'product':(string), 'revision':(string)},...]}
    |       |report      |{}   
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc'), 'cid': request.params.get('cid', '')}
    return groupGet(data, gid, uid)

@appweb.route('/group/<gid>/session/<sid>', method='POST', content_type='application/json', data_format=['subc', 'data'])
def doSessionPOST(gid,sid,uid):
    """
    URL:/group/<gid>/session/<sid>
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc   |data                   
    |       |create |{'planname':(string),'starttime':(string),
    |       |       | 'deviceinfo':{'deviceid':(string),'revision':(string),'product':(string), 'width':(int), 'height':(int)}}
    |       |update |{'endtime':(string)}
    |       |cycle  |{'cid':(int)cid}
    |       |delete |{}
    -----------------------------------------------------------------------------------------
    """
    return sessionPOST(request.json, gid, sid, uid)

@appweb.route('/group/<gid>/session/<sid>', method='GET')
def doSessionGET(gid, sid):
    """
    URL:/group/<gid>/session/<sid>
    TYPE:http/GET
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc       |data 
    |       |latest     |{'amount': (int)value}
    |       |history    |{'pagenumber': (int)value, 'pagesize': (int)value, 'casetype': (string)['total/pass/fail/error']}
    |       |poll       |{'tid': (int)value}
    |       |summary    |{}   
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc'), 'data':request.params}
    return sessionGET(data, gid, sid)

@appweb.route('/session/<sid>/case', method='POST', content_type='application/json', data_format=['subc', 'data'])
def doCasePOST(sid):
    """
    URL:/session/<sid>/case
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc    |data                                                          
    |       |create  |{'tid':(int), 'casename':(string), 'starttime':(string)}
    |       |update  |{'tid':(int)/(list), 'result':['Pass'/'Fail'/'Error'],
    |       |        | 'endtime':(string), 'traceinfo':(string), 'comments': (dict)}
    -----------------------------------------------------------------------------------------
    """
    return casePOST(request.json, sid)

@appweb.route('/session/<sid>/case/<tid>/file', method='PUT', content_type=['application/zip', 'image/png'], login=False)
def doCaseFilePUT(sid, tid):
    """
    URL:/session/<sid>/case/<tid>/file
    TYPE:http/PUT
    @fileData type: binary stream
    @param: content of file (zipped log/snapshot)
    @rtype:JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc         |data                                                          
    |       |uploadpng    |{}
    |       |uploadzip    |{}
    -----------------------------------------------------------------------------------------
    """
    subc = 'uploadpng' if 'image/png' in request.content_type else 'uploadzip'
    xtype = request.headers.get('Ext-Type') or ''
    return caseFilePUT(subc, sid, tid, request.body, xtype)

@appweb.route('/file/<fileid>', method='GET', login=False)
def doFileGET(fileid):
    """
    URL:/file/<fid>
    TYPE:http/GET
    @data type: string
    @param fileid: the unique id of case file
    @rtype: image/png, application/zip
    @return: image(bytes), attachment
    """
    data = fileGET(fileid)
    if data['result'] == 'error':
        return data
    else:
        if data['data']['content_type'] in ['image/png', 'image/jpg', 'image/jpeg']:
            response.set_header('Content-Type', data['data']['content_type'])
            return data['data']['filedata']
        elif data['data']['content_type'] in ['application/zip']:
            response.set_header('Content-Type', 'application/x-download')
            response.set_header('Content-Disposition', 'attachment; filename=' + data['data']['filename'])
            return data['data']['filedata']

@appweb.route('/file', method='PUT', login=False)
def doFilePUT():
    """
    URL:/file
    TYPE:http/PUT
    @rtype: string
    @return: URL to fetch file back
    """
    content_type = request.content_type
    filedata = request.body
    return filePUT(content_type, filedata)

@appweb.route('/session/<sid>/uploadresult', method='POST', content_type='multipart/form-data')
def doUploadSessionResult(sid):
    """
    URL:/group/<gid>/session/<sid>/uploadresult
    TYPE:http/POST
    @data type:form-data
    @param: result file
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc        |data                   
    |       |uploadXML   |filedata
    -----------------------------------------------------------------------------------------
    """
    return uploadSessionResult(request.files.get('file').file, sid)

@appweb.route('/account/active', method='GET')
def doAccountActive(uid):
    """
    URL:/account/active
    TYPE:http/POST
    @data type: JSON
    @param: token
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc        |data                   
    -----------------------------------------------------------------------------------------
    """
    return accountActive(uid)


if __name__ == '__main__':
    print 'WebServer Serving on 8080...'
    WSGIServer(("", 8080), appweb).serve_forever()