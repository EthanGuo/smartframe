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


@appweb.route('/account', method='POST', content_type='application/json', data_format=['subc', 'data'], login=False)
def doAccountWithOutUid():
    """
    URL:/account
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ---------------------------------------------------------------------------------------
    |support|subc          |data
    |       |register      |{'username':(string)username, 'password':(string)password, 'appid':(string)appid,'info':{'email':(string), 'telephone':(string)telephone, 'company':(string)company}
    |       |forgotpasswd  |{'email':(string)mailaddress}
    |       |login         |{'appid':(string)appid, 'username':(string)username, 'password':(string)password}
    ---------------------------------------------------------------------------------------
    """
    return accountWithOutUid(request.json)

@appweb.route('/user/<uid>', method='POST',content_type=['application/json','multipart/form-data'], data_format=['subc', 'data'])
def doAccountWithUid(uid):
    """
    URL:/user/<uid>
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc          |data
    |       |changepasswd  |{'oldpassword':(string)oldpassword, 'newpassword':(string)newpassword }
    |       |update        |{'info':{'email':(string), 'telephone':(string)telephone, 'company':(string)company}}
    |       |invite        |{'email':(string)email}
    |       |logout        |{}
    -----------------------------------------------------------------------------------------
    """
    return accountWithUid(request.json, uid)

@appweb.route('/user/<uid>', method='GET')
def doGetAccountInfo(uid):
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
    |       |list          |null  |{'count':(int)value, 'users':[{'uid':(string)uid,'username':(string)username},{'uid':(string)uid,'username':(string)username}]}}
    |       |info          |null  |{'username':(string)username,'inGroups':[{'gid':gid1,'groupname':(string)name1},{'gid':gid2,'groupname':(string)name2},...],'info':{'email':(string)email, 'telephone':(string)telephone, 'company':(string)company}}
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc')}
    return getAccountInfo(data, uid)

@appweb.route('/group', method='POST',content_type='application/json', data_format=['subc', 'data'])
def doGroupAction(uid):
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
    |       |create        |{'groupname':(string)name} 
    |       |delete        |{'gid':(int)gid}
    -----------------------------------------------------------------------------------------
    """
    return groupBasicAction(request.json, uid)

@appweb.route('/group/<gid>/member', method='POST', content_type='application/json', data_format=['subc', 'data'])
def doGroupMemberAction(gid, uid):
    """
    URL:/group/<gid>/member
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc          |data 
    |       |addmember     |{'members':[{'uid':(int)uid,'role':(int)roleId}]}  
    |       |setmember     |{'members':[{'uid':(int)uid,'role':(int)roleId}]}
    |       |delmember     |{'members':[{'uid':(int)uid,'role':(int)roleId}]}
    -----------------------------------------------------------------------------------------
    """
    return groupMemberAction(request.json, gid, uid)

@appweb.route('/group/<gid>/info', method='GET')
def doGetGroupInfo(gid, uid):
    """
    URL:/group/<gid>/info
    TYPE:http/GET
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc            |data 
    |       |info            |{}   
    |       |sessionsummary  |{}
    |       |cyclereport     |{}   
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc'), 'cid': request.params.get('cid', '')}
    return getGroupInfo(data, gid, uid)

@appweb.route('/group/<gid>/session/<sid>', method='POST', content_type='application/json',data_format=['subc', 'data'])
def doTestSessionAction(gid,sid,uid):
    """
    URL:/group/<gid>/test/<sid>
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc   |data                   
    |       |create |{'planname':(string)value,'starttime':(string)value,'deviceinfo':{'id':(string)id,'revision':(string)revision,'product':(string)product, 'width':(int)width, 'height':(int)height}}
    |       |update |{'cid':(int)cid,'endtime':(string)endtime, 'status':(string)status}
    |       |delete |{}
    -----------------------------------------------------------------------------------------
    """
    return testSessionBasicAction(request.json, gid, sid, uid)

@appweb.route('/group/<gid>/session/<sid>', method='GET')
def doGetSessionAction(gid, sid):
    """
    URL:/group/<gid>/test/<sid>
    TYPE:http/GET
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc         |data 
    |       |live         |
    |       |history      |
    |       |update       |
    |       |summary      |{}   
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc'), 'data':''}
    return getSessionAction(data, gid, sid)

@appweb.route('/group/<gid>/session/<sid>/case', method='POST', content_type='application/json', data_format=['subc', 'data'])
def doCaseResultAction(gid,sid):
    """
    URL:/group/<gid>/session/<sid>/case
    TYPE:http/POST
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc    |data                                                          
    |       |create  |{'tid':(int)tid, 'caseName':(string)value, 'starttime':(string)timestamp}
    |       |update  |{'tid':(int)/(list)tid, 'result':['Pass'/'Fail'/'Error'],'endtime':(string)endtime, 'traceinfo':(string)traceinfo, 'comments': (dict)comments}
    -----------------------------------------------------------------------------------------
    """
    return caseResultAction(request.json, gid, sid)

@appweb.route('/group/<gid>/session/<sid>/case/<tid>/fileupload', method='PUT', content_type=['application/zip', 'image/png'], login=False)
def doUploadCaseFile(gid, sid, tid):
    """
    URL:/group/<gid>/session/<sid>/case/<tid>/fileupload
    TYPE:http/PUT
    @fileData type: binary stream
    @param: content of file (zipped log/snapshot)
    @rtype:JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    """
    subc = 'uploadpng' if 'image/png' in request.content_type else 'uploadzip'
    xtype = request.headers.get('Ext-Type') or ''
    return uploadCaseResultFile(subc, gid, sid, tid, request.body, xtype)

@appweb.route('/snap/<imageid>', method='GET', login=False)
def doGetCaseImage(imageid):
    """
    URL:/snap/<fid>
    TYPE:http/GET
    @data type: string
    @param imageid: the unique id of case snap
    @rtype: image/png
    @return: image(bytes)
    """
    data = getSnapData(imageid)
    if isinstance(data, type({})):
        return data
    else:
        response.set_header('Content-Type', 'image/png')
        return data

@appweb.route('/group/<gid>/session/<sid>/case/<tid>/getsnaps', method='GET')
def doGetCaseResultSnapshots(gid, sid, tid):
    """
    URL:/group/<gid>/session/<sid>/case/<tid>/getsnaps
    TYPE:http/GET
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    """
    return getTestCaseSnaps(gid, sid, tid)

@appweb.route('/group/<gid>/session/<sid>/case/<tid>/getlog', method='GET')
def doGetCaseResultLog(gid, sid, tid):
    """
    URL:/group/<gid>/session/<sid>/case/<tid>/getlog
    TYPE:http/GET
    @data type:JSON
    @param:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{}, 'msg': '(string)info'}
    """
    result = getTestCaseLog(gid, sid, tid)
    if result['result'] == 'ok':
        filename = 'log-%s.zip' %tid
        response.set_header('Content-Type', 'application/x-download')
        response.set_header('Content-Disposition', 'attachment; filename=' + filename)
        return result['data']
    else:
        return result

if __name__ == '__main__':
    print 'WebServer Serving on 8080...'
    WSGIServer(("", 8080), appweb).serve_forever()

# @appweb.route('/account/active', method='POST', content_type='application/json')
# def doActiveUser(uid, token):
#     return null
