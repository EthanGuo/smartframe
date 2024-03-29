from bottle import request, Bottle, abort
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler, WebSocketError
from impl.test import *
from impl.device import *
from impl.auth import *
import time, uuid

app = Bottle()

###########################Test Server APIS##############################
@app.route('/user/register',method='POST')
def doRegister():
    """
    URL:/user/register
    TYPE:http/POST

    register a new account to server-side

    @type appid:string
    @param appid:the id of app/domain
    @type user:string
    @param user:the userName of account
    @type pswd:string
    @param pswd:the password of account
    @type info:JSON
    @param info:the info of account  
    @rtype: JSON
    @return: ok-{'results':1}
             error-{'errors':{'code':0,'msg':(string)info}} 
    """
    content_type = request.headers.get('Content-Type')
    if not (content_type):
        return {'errors':{'code':500, 'msg':'Missing Content-Type'}}
    else:
        json = request.json
        if not json is None:
            appid = json['appid']
            username = json['username']
            password = json['password']
            userinfo = json['info']
        else:
            appid = 'smartrunner'
            username = 'tester'
            password = '654321'
            userinfo = {'email':'smartrunner@borqs.com', 'contact':'+8613911312632'}
        return userRegister(appid,username,password,userinfo)

@app.route('/user/auth',method='POST')
def doAuth():
    """
    URL:/user/auth
    TYPE:http/POST

    Get access token by username and password

    @type appid:string
    @param appid:the id of app/domain
    @type user:string
    @param user:the userName of account
    @type pswd:string
    @param pswd:the password of account
    @rtype: JSON
    @return: ok-{'results':{'token':(string)value}}
             error-{'errors':{'code':0,'msg':(string)info}} 
    """
    content_type = request.headers.get('Content-Type')
    if not (content_type):
        return {'errors':{'code':500, 'msg':'Missing Content-Type'}}
    else:
        json = request.json
        if not json is None:
            appid = json['appid']
            username = json['username']
            password = json['password']
        else:
            appid = 'smartrunner'
            username = 'tester'
            password = '654321'           
        return userAuth(appid,username,password)

@app.route('/test/session/<sid>/create',method='POST')
def doCreateSession(sid):
    """
    URL:/test/session/<sid>/create
    TYPE:http/POST

    upload a test session to server.

    @type data:JSON
    @param data:{'token':(string)value,
                'starttime':(string)timevalue,
                'planname':(string)value,
                'deviceinfo':{'deviceid':(string)value,'product':(string)value,'buildversion':(string)value,'height':(int)value,'width':(int)value}}
    @rtype: JSON
    @return:ok-{'results':1}
            error-{'errors':{'code':value,'msg':(string)info}}
    """
    content_type = request.headers.get('Content-Type')
    if not (content_type):
        return {'errors':{'code':500, 'msg':'Missing Content-Type'}}
    else:
        json = request.json
        if not json is None:
            token = json['token']  
            planname = json['planname']  
            starttime = json['starttime']
            deviceid = json['deviceid']            
            deviceinfo = json['deviceinfo'] 
        else:
            token = '1122334455667788'      
            planname = 'testplan'
            starttime = time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime(time.time()))
            deviceid = '0123456789ABCDEF'
            deviceinfo = {'product':'AT390', 'revision':'6628', 'width':480, 'height':800}
        return createTestSession(token, sid, planname, starttime, deviceid, deviceinfo)

@app.route('/test/caseresult/<sid>/<tid>/create',method='POST')
def doCreateTestResult(sid, tid):
    """
    URL:/test/caseresult/<sid>/<tid>/create
    TYPE:http/POST
    
    Creating a test case result.

    @type sid:string
    @param sid:the id of test session
    @type  tid: string
    @param tid: the id of case result
    @type data:JSON
    @param data:{'token':(string)value,'caseName':(string)value, 'starttime':(string)timestamp}
    @rtype:JSON
    @return:ok-{'results':1}
            error-{'errors':{'code':value,'msg':(string)info}}
    """
    content_type = request.headers.get('Content-Type')
    if not (content_type):
        return {'errors':{'code':500, 'msg':'Missing Content-Type'}}
    else:
        json = request.json
        if not json is None:
            token = json['token'] 
            casename = json['casename']
            starttime = json['starttime']
        else:
            token = '112233445566'
            casename = 'MOCall.testcase'
            starttime = time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime(time.time()))
        return createCaseResult(token, sid, tid, casename, starttime)

@app.route('/test/caseresult/<sid>/<tid>/update',method='POST')
def doUpdateTestResult(sid, tid):
    """
    URL:/test/caseresult/<sid>/<tid>/update
    TYPE:http/POST

    Update the test case result by the tid of test case.

    @type sid:string
    @param sid:the id of test session
    @type  tid: string
    @param tid: the id of case result
    @type data:JSON
    @param data:{'token':(string)value,'result':value ['Pass'/'Fail'/'Error'],'time':(string)timestamp}
    @rtype:JSON
    @return:ok-{'results':1}
            error-{'errors':{'code':value,'msg':(string)info}}
    """
    content_type = request.headers.get('Content-Type')
    if not (content_type):
        return {'errors':{'code':500, 'msg':'Missing Content-Type'}}
    else:
        json = request.json
        if not json is None:
            token = json['token'] 
            status = json['result']         
        else:
            token = '1122334455667788'
            status = 'Pass'
        return updateCaseResult(token, sid, tid, status)

@app.route('/test/caseresult/<sid>/<tid>/fileupload',method='PUT')
def doUploadFile(sid, tid):
    """
    URL:/test/caseresult/<sid>/<tid>/fileupload
    TYPE:http/PUT

    Update the test case result by the tid of test case.

    @type sid:string
    @param sid:the id of test session
    @type  tid: string
    @param tid: the id of case result
    @type data:JSON
    @param data:{'token':(string)value}
    @type fileData:binary stream
    @param fileData:content of file (logzip/snapshot)    
    @rtype:JSON
    @return:ok-{'results':1}
            error-{'errors':{'code':value,'msg':(string)info}}
    """
    content_type = request.headers.get('Content-Type')
    token = request.headers.get('token')
    if not (content_type):
        return {'errors':{'code':500, 'msg':'Missing Content-Type'}}
    elif not (token):
        return {'errors':{'code':500, 'msg':'Missing token'}}        
    else:
        if content_type == 'image/png':
            ftype = 'png'
        else:
            ftype = 'zip'
        rawdata = request.body.read()
        return uploadCaseResultFile(token, sid, tid, rawdata, ftype)

if __name__ == '__main__':
    WSGIServer(("", 8081), app, handler_class=WebSocketHandler).serve_forever()