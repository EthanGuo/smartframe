#!/usr/bin/env python

#from pymongo import Connection
import gridfs
import memcache
import hashlib,uuid,base64
from bson.objectid import ObjectId
from datetime import datetime
import pymongo
from pymongo import *
from pymongo import ReplicaSetConnection
from pymongo.read_preferences import ReadPreference
from pymongo import ReadPreference
from pymongo.errors import AutoReconnect

DATE_FORMAT_STR1 = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_STR = "%Y.%m.%d-%H.%M.%S"
IDLE_TIME_OUT = 1800

def getMongoDB(connstr,replica):
    conn = ReplicaSetConnection(connstr, replicaSet=replica)
    conn.read_preference = ReadPreference.SECONDARY_PREFERRED
    #conn = Connection(server,port)
    db = conn.smartServer
    return db

def getGridFS(connstr,replica):
    conn = ReplicaSetConnection(connstr, replicaSet=replica)
    conn.read_preference = ReadPreference.SECONDARY_PREFERRED
    #conn = Connection(server,port)
    fs = gridfs.GridFS(conn.smartFiles, collection='fs')
    return fs 
    
def getMemcache(connstr,debugOn):
    mc = memcache.Client([connstr], debug=debugOn)
    return mc

class testStore(object):
    """
    Class dbStore provides the access to MongoDB DataBase
    """
    def __init__(self, db, fs, mem):
        """
        do the database instance init works
        """
        print 'init db store class!!!'
        self._db = db
        self._fs = fs
        self._mc = mem
        self._snapqueue = {}

    def counter(self, keyname):  
        ret = self._db.counter.find_and_modify(query={"_id":keyname},update={"$inc":{"next":1}},new=True,upsert=True)
        return int(ret["next"]);

    def getfile(self,fileId):
        '''
        Get file.
        '''
        data = None
        objId = ObjectId(fileId)
        exists = self._fs.exists(objId)
        if exists:
            data = self._fs.get(objId)
        return data

    def setfile(self,data):
        '''
        Get file.
        '''
        fid = self._fs.put(data)
        return str(fid)

    def deletefile(self,fileId):
        '''
        Delete file.
        '''
        objId = ObjectId(fileId)
        self._fs.delete(objId)

    def setCache(self,key,value=None):
        '''
        set Cache value.
        '''
        if not self._mc is None:
            self._mc.set(key,value)
            return key
        else:
            return None

    def getCache(self,key):
        '''
        get Cache value.
        '''
        if not self._mc is None:
            value = self._mc.get(key)
            return value
        else:
            return None

    def createUser(self,appid,user,password,info):
        """
        write a user account record in database
        """
        uid = ''
        users = self._db['users']
        tokens = self._db['tokens']
        ret = users.find_one({'username':user})
        if not ret is None:
            return {'code':'04', 'msg':'An account with same username already registered!'} 

        ret = users.find_one({'info.email':info['email']})
        if not ret is None:
            return {'code':'04', 'msg':'An account with same email already registered!'}

        m = hashlib.md5()
        m.update(password)
        pswd = m.hexdigest()
        m.update('%08d' % self.counter('userid'))
        uid = m.hexdigest()
        users.insert({'uid':uid,'appid':appid,'username':user,'password':pswd,'active':False,'info':info})
        m = hashlib.md5()
        m.update(str(uuid.uuid1()))
        token = m.hexdigest()
        tokens.insert({'uid':uid,'appid':'00','token':token,'expires':'300000'})
        return {'uid':uid,'token':token}

    def createGroup(self,groupname,info):
        """
        write a user account record in database
        """
        gid = ''
        groups = self._db['groups']
        ret = groups.find({'groupname':groupname})
        for d in ret:
            gid = d['gid']

        if gid != '':
            return {'code':'04', 'msg':'A group with same username exists!'}            
        else:        
            m = hashlib.md5()
            m.update('%08d' % self.counter('groupid'))
            gid = m.hexdigest()  
            groups.insert({'gid':gid,'groupname':groupname,'info':info})
            return {'gid':gid}

    def addGroupMember(self,gid,uid,role):
        members = self._db['group_members']
        vrole = None
        ret = members.find({'gid':gid,'uid':uid})
        for d in ret:
            vrole = d['role']

        if not vrole is None:
            members.update({'gid':gid,'uid':uid},{'$set':{'role':role}})        
        else:
            members.insert({'gid':gid,'uid':uid,'role':role})
        return {'gid':gid}

    def setGroupMember(self,gid,uid,role):
        members = self._db['group_members']
        members.update({'gid':gid,'uid':uid},{'$set':{'role':role}})
        return {'gid':gid}

    def delGroupMember(self,gid,uid):
        members = self._db['group_members']
        members.remove({'gid':gid,'uid':uid})
        return {'gid':gid}

    def getUserRole(self,gid,uid):
        members = self._db['group_members']
        retdata = members.find({'gid':gid,'uid':uid})
        result = {}
        for d in retdata:
            result = {'uid':d['uid'],'role':d['role']}
        return result

    def getGroupInfo(self,gid):
        result = {}
        lstmember = []
        groups = self._db['groups']
        members = self._db['group_members']
        users = self._db['users']
        retdata = groups.find({'gid':gid})
        for t in retdata:
            retmember = members.find({'gid':gid})
            for d in retmember:
                retuser = users.find({'uid':d['uid']})
                username = ''
                for k in retuser: username = k['username']
                lstmember.append({'uid':d['uid'],'username':username,'role':d['role']})
            result = {'gid':t['gid'],'groupname':t['groupname'],'info':t['info'], 'members':lstmember}      
        return result

    def userInfo(self,uid):
        baseinfo = {}
        ingroups = []
        groupname = 'N/A'
        users = self._db['users']
        groups = self._db['groups']
        retData = users.find({'uid':uid})
        for t in retData:
            members = self._db['group_members']
            retgroup = members.find({'uid':uid})
            for d in retgroup:
                retname = groups.find({'gid':d['gid']})
                for k in retname:
                    groupname = k['groupname']
                ingroups.append({'gid':d['gid'],'groupname':groupname,'role':d['role']})  
            result = {'uid':t['uid'],'username':t['username'],'info':t['info'], 'inGroups':ingroups}
        return result

    def userChangePassword(self,uid,oldpassword,newpassword):
        m = hashlib.md5()
        m.update(oldpassword)
        rdata = users.findOne({'uid':uid})
        if m.hexdigest() == rdata['password']:
            m.update(newpassword)
            users.update({'uid':uid},{'$set':{'password':m.hexdigest()}})
            return {'uid':uid}
        else:
            return {'code':'03', 'msg':'Invalid original password!'}

    def userUpdateInfo(self,uid,info):
        users = self._db['users']
        users.update({'uid':uid},{'$set':{'info':info}})
        return {'uid':uid}

    def userExists(self,username,password):
        users = self._db['users']
        if '@' in username:
            rdata = users.find_one({'info.email':username,'password':password})
        else:
            rdata = users.find_one({'username':username,'password':password})
        if not rdata is None:
            return rdata['uid']
        else:
            return None

    def activeUser(self,uid):
        users = self._db['users']
        users.update({'uid':uid},{'$set':{'active':True}})
        return {'uid':uid}

    def getUserList(self):
        results = {}
        lists = []
        users = self._db['users']
        rdata = users.find()
        lists = [{'uid':d['uid'],'username':d['username']} for d in rdata]
        results['count'] = len(lists)
        results['users'] = lists
        return results

    def validToken(self, token):
        uid = ''
        username = ''
        tokens = self._db['tokens']
        rdata = tokens.find({'token':token})
        for t in rdata:
            uid = t['uid']
 
        if uid != '':
            users = self._db['users']
            rdata = users.find_one({'uid':uid})
            if not rdata is None:
                username = rdata['username']
            return {'uid':uid, 'username':username}  
        else:
            return {'code':'02', 'msg':'Invalid token!'} 

    def createToken(self, appid, uid, info, expires):
        """
        write a user account record in database
        """
        tokens = self._db['tokens']
        rdata = tokens.find_one({'appid':appid,'uid':uid})
        if not rdata is None:
            token = rdata['token']
        else:
            m = hashlib.md5()
            m.update(str(uuid.uuid1()))
            token = m.hexdigest()
            tokens.insert({'appid':appid,'uid':uid,'info':info,'token':token,'expires':expires})
        return {'token':token,'uid':uid}

    def deleteToken(self,token):
        tokens = self._db['tokens']
        tokens.remove({'token':token})

    def createTestSession(self, gid, sid, uid, planname, starttime, deviceid, devinfo):
        """
        write a test session record in database
        """
        _id = self.counter('group'+gid)
        session = self._db['testsessions']
        session.insert({'_id':_id,
                       'gid':gid,
                       'sid':sid,
                       'tester':uid,
                       'planname':planname,
                       'starttime':starttime,
                       'endtime': 'N/A', 
                       'runtime': 0,
                       'summary':{'total':0,'pass':0,'fail':0,'error':0},
                       'deviceid':deviceid,
                       'deviceinfo':devinfo
                      });

    def updateTestSession(self,gid,sid,endtime):
        """
        write a test session record in database
        """
        session = self._db['testsessions']
        session.update({'gid':gid,'sid':sid},{'$set':{'endtime':endtime}});        

    def deleteTestSession(self,gid, sid):
        """
        delete a test session from database
        """
        caseresult = self._db['testresults']
        caseresult.remove({'gid':gid,'sid':sid});
        session = self._db['testsessions']
        session.remove({'gid':gid, 'sid':sid});

    def readTestSessionList(self, gid):
        """
        read list of test session records in database
        """
        users = self._db['users']
        user = 'N/A'
        session = self._db['testsessions']
        rdata = session.find({'gid':gid})
        result = {}
        dtnow = datetime.now()
        lists = []
        for d in rdata:
            if d['endtime'] == 'N/A':
                dttime = self.getCache(str('sid:'+d['sid']+':uptime'))
                if dttime is None:
                    idletime = IDLE_TIME_OUT
                else:
                    try:
                        idle = datetime.strptime(dttime, DATE_FORMAT_STR1)
                    except:
                        idle = datetime.strptime(dttime, DATE_FORMAT_STR)
                    delta = dtnow - idle
                    idletime = delta.days * 86400 + delta.seconds
                
                if idletime >= IDLE_TIME_OUT:
                    d['endtime'] = 'idle'

            rrdata = users.find({'uid':d['tester']})
            for dd in rrdata:
                user = dd['username']

            lists.append({'_id':d['_id'],
                         'sid':d['sid'],
                         'gid':d['gid'],
                         'tester':user,
                         'planname':d['planname'],
                         'starttime':d['starttime'],
                         'endtime':d['endtime'],
                         'runtime':d['runtime'],
                         'summary':d['summary'],
                         'deviceid':d['deviceid'],
                         'deviceinfo':d['deviceinfo']})
        result['count'] = len(lists)
        result['sessions'] = lists
        return result

    def readTestSessionInfo(self,gid,sid):
        """
        read list of test session records in database
        """
        users = self._db['users']
        user = 'N/A'
        session = self._db['testsessions']
        rdata = session.find({'gid':gid,'sid':sid})
        
        dtnow = datetime.now()
        for d in rdata:
            if d['endtime'] == 'N/A':
                dttime = self.getCache(str('sid:'+d['sid']+':uptime'))
                if dttime is None:
                    idletime = IDLE_TIME_OUT
                else:
                    try:
                        idle = datetime.strptime(dttime, DATE_FORMAT_STR1)
                    except:
                        idle = datetime.strptime(dttime, DATE_FORMAT_STR)
                    delta = dtnow - idle
                    idletime = delta.days * 86400 + delta.seconds

                if idletime >= IDLE_TIME_OUT:
                    d['endtime'] = 'idle'

            rrdata = users.find({'uid':d['tester']})
            for dd in rrdata:
                user = dd['username']

            result = {'_id':d['_id'],
                      'gid':d['gid'],        
                      'sid':d['sid'],
                      'tester':user,
                      'planname':d['planname'],
                      'starttime':d['starttime'],
                      'endtime':d['endtime'],
                      'runtime':d['runtime'],
                      'summary':d['summary'],
                      'deviceid':d['deviceid'],
                      'deviceinfo':d['deviceinfo']}

        caseresult = self._db['testresults']
        rdata = caseresult.find({'sid':sid})
        lists = [{'tid':d['tid'],
                  'gid':d['gid'],
                  'sid':d['sid'],
                  'casename':d['casename'],
                  'starttime':d['starttime'],
                  'endtime':d['endtime'],
                  'traceinfo':d['traceinfo'],
                  'result':d['result']} for d in rdata]
        result['count'] = len(lists)
        result['cases'] = lists
        return result

    def readTestCaseInfo(self, gid, sid, tid):
        """
        read list of test cases records in database
        """
        caseresult = self._db['testresults']
        ret = caseresult.find({'sid':sid,'tid':tid})
        result = None
        for d in ret:
            if not 'result' in d :
                d['result'] = ''
            if not 'log' in d :
                d['log'] = ''
            if not 'snapshots' in d:
                d['snapshots'] = []
            if not 'checksnap' in d:
                d['checksnap'] = ''

            result = {'tid':d['tid'],
                    'casename':d['casename'],
                    'starttime':d['starttime'],
                    'endtime':d['endtime'],
                    'result':d['result'],
                    'traceinfo':d['traceinfo'],
                    'log':d['log'],
                    'snapshots':d['snapshots'],
                    'checksnap':d['checksnap']}
        return result

    def getCaseLog(self, gid, sid, tid):
        """
        read list of test session records in database
        """
        caseresult = self._db['testresults']
        ret = caseresult.find({'sid':sid,'tid':tid})
        result = None
        logid = None
        for d in ret:
            logid = d['log'] 
        if not logid is None:
            result = self.getfile(logid)
        return result

    def createTestCaseResult(self, gid, sid, tid, casename, starttime):
        """
        write a test case resut record in database
        """
        self._snapqueue[sid+'-'+tid] = []
        timestamp = datetime.now().strftime(DATE_FORMAT_STR1)
        self.setCache(str('sid:'+ sid + ':uptime'), timestamp)
        caseresult = self._db['testresults']
        caseresult.insert({'gid':gid,'sid':sid, 'tid':tid, 'casename':casename, 'log':'N/A', 'traceinfo':'N/A','result':'running', 'starttime':starttime, 'endtime':'N/A','snapshots':[]})
        session = self._db['testsessions']
        session.update({'gid':gid,'sid':sid},{'$inc':{'summary.total':1}})

    def updateTestCaseResult(self, gid, sid, tid, status, traceinfo, endtime):
        """
        update a test case resut record in database
        If case get failed, write snapshot png files in GridFS
        """
        timestamp = datetime.now().strftime(DATE_FORMAT_STR1)
        self.setCache(str('sid:'+ sid + ':uptime'),timestamp)
        caseresult = self._db['testresults']
        session = self._db['testsessions']
        status = status.lower()
        runtime = 0
        snapshots = self._snapqueue[sid+'-'+tid]
        rdata = session.find({'sid':sid})
        for d in rdata:
            starttime = d['starttime']             
            try:
                d1 = datetime.strptime(starttime, DATE_FORMAT_STR)
            except:
                d1 = datetime.strptime(starttime, DATE_FORMAT_STR1)
            try:
                d2 = datetime.strptime(endtime, DATE_FORMAT_STR)
            except:
                d2 = datetime.strptime(endtime, DATE_FORMAT_STR1)

            delta = d2 - d1
            runtime = delta.days*86400 + delta.seconds

        if status == 'pass':
            for d in snapshots:
                self.deletefile(d['fid'])
            snapshots = []
            session.update({'gid':gid,'sid':sid},{'$inc':{'summary.pass':1},'$set':{'runtime':runtime}})
        elif status == 'fail':
            session.update({'gid':gid,'sid':sid},{'$inc':{'summary.fail':1},'$set':{'runtime':runtime}})               
        else:
            session.update({'gid':gid,'sid':sid},{'$inc':{'summary.error':1},'$set':{'runtime':runtime}})

        caseresult.update({'gid':gid,'sid':sid,'tid':tid},{'$set':{'result':status,'traceinfo':traceinfo,'endtime':endtime,'snapshots':snapshots}})

    def writeTestLog(self, gid, sid, tid, logfile):
        """
        add log file in GridFS
        update the corresponding test case resut record
        """
        caseresult = self._db['testresults']
        fkey = self.setfile(logfile)
        caseresult.update({'gid':gid,'sid':sid,'tid':tid},{'$set':{'log':fkey}})

    def writeTestSnapshot(self, gid, sid, tid, snapfile, stype):
        """
        add snapshot png in image buffer
        """
        self.setCache(str('sid:'+sid+':snap'), snapfile)
        timenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.setCache(str('sid:'+sid+':snaptime'),timenow)

        if not (sid+'-'+tid) in self._snapqueue:
            self._snapqueue[sid+'-'+tid] = []

        try:
            results = self._db['testresults']
            posi = stype.index(':')
            xtype = stype[0:posi]
            sfile = stype[posi+1:]
            fkey = self.setfile(snapfile)
            if xtype == 'expect':
                results.update({'gid':gid,'sid':sid,'tid':tid}, {'$set':{'checksnap':{ 'title':sfile,'fid':fkey }}})
            elif xtype == 'current':
                self._snapqueue[sid+'-'+tid].append({'title':sfile, 'fid':fkey})
        except:
            pass
    
    def readTestLiveSnaps(self,gid, sid):
        result = []
        snap = self.getCache(str('sid:'+sid+':snap'))
        snaptime = self.getCache(str('sid:'+sid+':snaptime'))
        if not snap is None:
            result.append({'snap':snap, 'snaptime':snaptime})
        return result

    def readTestHistorySnaps(self, gid, sid, tid):
        caseresult = self._db['testresults']
        ret = caseresult.find({'sid':sid,'tid':tid})
        snapids = []
        snaps = []
        checkid = ''
        checksnap = ''
        stitle = ''
        for d in ret:
            snapids = d['snapshots']
            if not 'checksnap' in d:
                checkid = ''
                stitle = ''
            else:
                stitle = d['checksnap']['title']
                checkid = d['checksnap']['fid']
  
        if checkid != '':
            fs = self.getfile(checkid)
            if not fs is None:
                checksnap = {'title':stitle,'data': base64.encodestring(fs.read())}

        for d in snapids:
            stitle = d['title']
            fs = self.getfile(d['fid'])
            if not fs is None:
                snaps.append({'title':stitle,'data':base64.encodestring(fs.read())})   

        return {'snaps':snaps, 'checksnap':checksnap}


dbImpl = getMongoDB("192.168.5.60:27017,192.168.7.52:27017,192.168.5.156:27017","ats_rs")
fsImpl = getGridFS("192.168.5.60:27017,192.168.7.52:27017,192.168.5.156:27017","ats_rs")

#dbImpl = getMongoDB("192.168.7.212",27017)
#fsImpl = getGridFS("192.168.7.212",27017)

mcImpl = getMemcache("127.0.0.1:11211", 0)
store = testStore(dbImpl, fsImpl, mcImpl)

