#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent.pywsgi import WSGIServer
from bottle import request, Bottle, response
from plugins import ContentTypePlugin, DataFormatPlugin, LoginPlugin
from impl.mapping import *

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
    |       |register       |{'username':(string)username, 'password':(string)password, 'appid':(string)appid,'info':{'email':(string), 'telephone':(string)telephone, 'company':(string)company}
    |       |retrievepswd   |{'email':(string)mailaddress}
    |       |login          |{'appid':(string)appid, 'username':(string)username, 'password':(string)password}
    ---------------------------------------------------------------------------------------
    """
    return accountWithoutUid(request.json)

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
    |       |changepswd    |{'oldpassword':(string)oldpassword, 'newpassword':(string)newpassword }
    |       |update        |{'username':(string), 'telephone':(string)telephone, 'company':(string)company}
    |       |invite        |{'email':(string)email}
    |       |logout        |{}
    -----------------------------------------------------------------------------------------
    """
    if 'multipart/form-data' in request.content_type:
        data = {'subc': 'update'}
        data['data'] = {'file': request.files.get('data')}
    else:
        data = request.json
    return accountWithUid(data, uid)

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
    |support|subc          |data  |return data 
    |       |accountlist   |null  |{'count':(int)value, 'users':[{'uid':(string)uid,'username':(string)username},{'uid':(string)uid,'username':(string)username}]}}
    |       |accountinfo   |null  |{'username':(string)username,'info':{'email':(string)email, 'telephone':(string)telephone, 'company':(string)company}}
    |       |groups        |null  |{'groups':[{'gid':(int)gid1,'groupname':(string)name1, 'allsession': (int)count, 'livesession': (int)count},...]}
    |       |sessions      |null  |{'sessions': [{'sid':(int)sid, 'gid':(int)gid, 'groupname':(string)name},...]}
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc')}
    return getAccountInfo(data, uid)

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
    |       |create        |{'groupname':(string)name, 'info': }
    -----------------------------------------------------------------------------------------
    """
    return groupBasicAction(request.json, uid)

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
    |       |setmember     |{'members':[{'uid':(int)uid,'role':(int)roleId}]}
    |       |delmember     |{'members':[{'uid':(int)uid,'role':(int)roleId}]}
    -----------------------------------------------------------------------------------------
    """
    return groupMemberAction(request.json, gid, uid)

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
    |support|subc            |data 
    |       |members         |{}   
    |       |sessions        |{}
    |       |cycles          |{}
    |       |report          |{}   
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc'), 'cid': request.params.get('cid', '')}
    return getGroupInfo(data, gid, uid)

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
    |       |create |{'planname':(string)value,'starttime':(string)value,'deviceinfo':{'id':(string)id,'revision':(string)revision,'product':(string)product, 'width':(int)width, 'height':(int)height}}
    |       |update |{'endtime':(string)endtime, 'status':(string)status}
    |       |cycle  |{'cid':(int)cid}
    |       |delete |{}
    -----------------------------------------------------------------------------------------
    """
    return testSessionBasicAction(request.json, gid, sid, uid)

@appweb.route('/session/<sid>', method='GET')
def doSessionGET(gid, sid):
    """
    URL:/session/<sid>
    TYPE:http/GET
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc         |data 
    |       |latest       |{'amount': (int)value}
    |       |history      |{'pagenumber': (int)value, 'pagesize': (int)value, 'casetype': (string)['total/pass/fail/error']}
    |       |poll         |{'tid': (int)value}
    |       |summary      |{}   
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc'), 'data':request.params}
    return getSession(data, gid, sid)

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
    |       |create  |{'tid':(int)tid, 'casename':(string)value, 'starttime':(string)timestamp}
    |       |update  |{'tid':(int)/(list)tid, 'result':['Pass'/'Fail'/'Error'],'endtime':(string)endtime, 'traceinfo':(string)traceinfo, 'comments': (dict)comments}
    -----------------------------------------------------------------------------------------
    """
    return caseResultAction(request.json, sid)

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
    |support|subc           |data                                                          
    |       |uploadpng      |{}
    |       |uploadzip      |{}
    -----------------------------------------------------------------------------------------
    """
    subc = 'uploadpng' if 'image/png' in request.content_type else 'uploadzip'
    xtype = request.headers.get('Ext-Type') or ''
    return uploadCaseResultFile(subc, sid, tid, request.body, xtype)

@appweb.route('/file/<fileid>', method='GET')
def doFileGET(fileid):
    """
    URL:/file/<fid>
    TYPE:http/GET
    @data type: string
    @param fileid: the unique id of case file
    @rtype: image/png, application/zip
    @return: image(bytes), attachment
    """
    data = getFileData(fileid)
    if data['result'] == 'error':
        return data
    else:
        if data['data']['content_type'] in ['image/png', 'image/jpg', 'image/jpeg']:
            response.set_header('Content-Type', data['data']['content_type'])
            return data['data']['filedata']
        elif data['data']['content_type'] in ['application/zip']:
            response.set_header('Content-Type', 'application/x-download')
            response.set_header('Content-Disposition', 'attachment; filename=' + data['data']['filename'])
            return result['data']['filedata']

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
    return uploadFile(content_type, filedata)

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

if __name__ == '__main__':
    print 'WebServer Serving on 8080...'
    WSGIServer(("", 8080), appweb).serve_forever()