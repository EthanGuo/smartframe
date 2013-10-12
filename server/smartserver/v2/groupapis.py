#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent.pywsgi import WSGIServer
from bottle import request, Bottle
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
    @type data:JSON
    @param data:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
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
    @type data:JSON
    @param data:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
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
    @type data:JSON
    @param data:{'subc': '', 'data':{}}
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
    @data type: JSON
    @param: {'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
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
    @type data:JSON
    @param data:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
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
    @type data:JSON
    @param data:{'subc': '', 'data':{}}
    @rtype: JSON
    @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
             error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
    ----------------------------------------------------------------------------------------
    |support|subc          |data 
    |       |info          |{}   
    |       |testsummary   |{}   
    -----------------------------------------------------------------------------------------
    """
    data = {'subc': request.params.get('subc')}
    return getGroupInfo(data, gid, uid)


if __name__ == '__main__':
    print 'WebServer Serving on 8080...'
    WSGIServer(("", 8080), appweb).serve_forever()

# @appweb.route('/account/active', method='POST', content_type='application/json')
# def doActiveUser(uid, token):
#     return null

# @appweb.route('/group/<gid>/session/<sid>', method='POST', content_type='application/json')
# def doTestSessionAction(gid,sid):
#     """
#     URL:/group/<gid>/test/<sid>
#     TYPE:http/POST
#     @type data:JSON
#     @param data:{'subc': '', 'data':{}}
#     @rtype: JSON
#     @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
#              error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
#     ----------------------------------------------------------------------------------------
#     |support|subc   |data                   
#     |       |create |{'token':(string)token,'planname':(string)value,'starttime':(string)value,'deviceinfo':{'id':(string)id,'revision':(string)revision,'product':(string)product, 'width':(int)width, 'height':(int)height}}
#     |       |update |{'token':(string)token,'endtime':(string)endtime, 'status':(string)status}
#     |       |delete |{'token':(string)token,'gid':(string)gid, 'sid':(string)sid}
#     -----------------------------------------------------------------------------------------
#     """
#     return testSessionAction(gid,sid,request.json)

# # @appweb.route('/group/<gid>/test/<sid>/results', method='GET')
# # def doGetSessionInfo(gid, sid):   
# # @appweb.route('/group/<gid>/test/<sid>/live', method='GET')
# # def getSessionLiveData(gid, sid):
# # @appweb.route('/group/<gid>/test/<sid>/poll', method='GET')
# # def checkSessionUpdated(gid, sid):
# # @appweb.route('/group/<gid>/test/<sid>/history', method='GET')
# # def getSessionHistoryData(gid, sid):
# # @appweb.route('/group/<gid>/test/<sid>/summary', method='GET')
# # def doGetSessionSummary(gid, sid):

# @appweb.route('/group/<gid>/session/<sid>', method='GET')
# def doGetSessionAction(gid, sid):
#     """
#     URL:/group/<gid>/test/<sid>
#     TYPE:http/GET
#     @type data:JSON
#     @param data:{'subc': '', 'data':{}}
#     @rtype: JSON
#     @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
#              error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
#     ----------------------------------------------------------------------------------------
#     |support|subc    |data                                                          |return data
#     |       |result |{'token':(string)token,'gid':(string)gid, 'sid':(string)sid}} |:{'count':(int)count, 'paging':{'pagesize':(int)pagesize,'totalpage':(int)totalpage,'curpage':(int)curPage },'cases':[{'casename':(string)casename, 'starttime':(string)}, 'result':(pass,fail,error), 'log':(string)logfileKey, snaps':[]...]}}, 'msg': ''}
#     |       |summary |{'token':(string)token,'gid':(string)gid, 'sid':(string)sid}  |
#     -----------------------------------------------------------------------------------------
#     """
#     return getSessionAction(gid,sid,request.json)

# # @appweb.route('/group/<gid>/test/<sid>/case/<tid>/create', method='POST', content_type='application/json')
# # def doCreateCaseResult(gid, sid, tid):
# # @appweb.route('/group/<gid>/test/<sid>/case/<tid>/update', method='POST', content_type='application/json')
# # def doUpdateCaseResult(gid, sid, tid):

# @appweb.route('/group/<gid>/test/<sid>/case/<tid>', method='POST', content_type='application/json')
# def doCaseResultAction(gid,sid,tid):
#     """
#     URL:/group/<gid>/test/<sid>/case/<tid>
#     TYPE:http/POST
#     @type data:JSON
#     @param data:{'subc': '', 'data':{}}
#     @rtype: JSON
#     @return: ok-{'result':'ok', 'data':{}, 'msg': ''}
#              error-{'result':'error', 'data':{'code':(string)code}, 'msg': '(string)info'}
#     ----------------------------------------------------------------------------------------
#     |support|subc    |data                                                          
#     |       |create  |{'token':(string)value,'caseName':(string)value, 'starttime':(string)timestamp}
#     |       |update  |{'token':(string)value,'result':value ['Pass'/'Fail'/'Error'],'time':(string)timestamp}
#     -----------------------------------------------------------------------------------------
#     """
#     return caseResultAction(gid,sid,tid,request.json)

# @appweb.route('/group/<gid>/test/<sid>/case/<tid>/fileupload', method='PUT', content_type=['application/zip', 'image/png'], login=False)
# def doUploadCaseFile(gid, sid, tid):
#     return None

# @appweb.route('/group/<gid>/test/<sid>/case/<tid>/snaps', method='GET')
# def doGetCaseResultSnapshots(gid, sid, tid):
#     return getTestCaseSnaps(gid, sid, tid)
