#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smartserver.v2.impl.session import *
import unittest
from pymongo import MongoClient
from smartserver.v2.config import MONGODB_URI
from datetime import datetime

class TestSession(unittest.TestCase):
    def setUp(self):
        self._mc = MongoClient(MONGODB_URI)
        self.db = self._mc.smartServer_eth

    def _getTime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def testsessionCreate(self):
        gid, sid, uid = '1', '1', '1'
        data = {'planname': 'testPlan', 'starttime': self._getTime(), 'deviceinfo':{'revision': 'bkb-131022', 'product': 'BKB'}}
        sessionCreate(data, gid, sid, uid)
        self.assertTrue(self.db['Sessions'].find(gid=1, sid=1).count() == 1)

    def testsessionUpdate(self):
        data = {'cid': 0}
        gid, sid, uid = '1', '1', '1'
        self.db['Sessions'].insert({'gid': 1, 'sid': 1, 'uid': 1})

        result = sessionUpdate(data, gid, sid, uid)
        self.assertTrue(result['result'] == 'ok')
        sids = self.db['Cycles'].find({'gid': 1, 'cid': result['data']['cid']})[0]['sids']
        self.assertTrue(1 in sids)
        result = sessionUpdate(data, gid, sid, uid)
        self.assertTrue(result['result'] == 'error')

        data = {'cid': -1}
        result = sessionUpdate(data, gid, sid, uid)
        self.assertTrue(result['result'] == 'ok')
        result = sessionUpdate(data, gid, sid, uid)
        self.assertTrue(result['result'] == 'error')

        self.db['Cycles'].update({'cid': 1, 'gid': 1}, {'$set':{'sids': [1]}})
        self.db['Cycles'].insert({'cid': 2, 'gid': 1, 'sids': []})
        data = {'cid': 2}
        result = sessionUpdate(data, gid, sid, uid)
        self.assertTrue(result['result'] == 'ok')
        sids = self.db['Cycles'].find({'gid': 1, 'cid': result['data']['cid']})[0]['sids']
        self.assertTrue(1 in sids)
        sids = self.db['Cycles'].find({'gid': 1, 'cid': 1})[0]['sids']
        self.assertTrue(not 1 in sids)
        
        time = self._getTime()
        data = {'endtime': time}
        sessionUpdate(data, gid, sid, uid)
        result = self.db['Sessions'].find({'gid': 1, 'sid': 1})[0]['endtime'].strftime('%Y-%m-%d %H:%M:%S')
        self.assertTrue(time == result)

    def testsessionDelete(self):
        gid, sid, uid, data = '1', '1', '1', {}
        self.db['Groups'].insert({'groupname': 'testGroup', 'gid': 1})
        self.db['GroupMembers'].insert({'gid': 1, 'uid': 9, 'role': 9})
        self.db['Sessions'].insert({'gid': 1, 'sid': 1, 'uid': 1})
        
        sessionDelete(data, gid, sid, uid)
        self.assertTrue(self.db['Sessions'].find({'gid': 1, 'sid': 1}).count() == 0)

        self.db['Sessions'].insert({'gid': 1, 'sid': 1, 'uid': 1})
        uid = '2'

        sessionDelete(data, gid, sid, uid)
        self.assertTrue(self.db['Sessions'].find({'gid': 1, 'sid': 1}).count() == 1)

    def testsessionSummary(self):
        self.db['Users'].insert({'username': 'test', 'uid': 1})
        self.db['Sessions'].insert({'gid': 1, 'sid': 1, 'uid': 1, 'planname': 'Test'})

        result = sessionSummary({}, '1', '1')
        self.assertTrue(result['result'] == 'ok')

    def _insertCases(self, count):
        for i in range(1, count):
            self.db['Cases'].insert({'gid': 1, 'sid': 1, 'tid': i, 'casename': 'wifi.testOpenWifi_' + str(i), 'result': 'pass'})

    def testsessionPollStatus(self):
        self._insertCases(10)
        data, gid, sid = {'tid': 8}, '1', '1'

        result = sessionPollStatus(data, gid, sid)
        self.assertTrue(result['result'] == 'ok')

        data = {'tid': 9}
        result = sessionPollStatus(data, gid, sid)
        self.assertTrue(result['result'] == 'error')
        
    def testsessionGetLatestCases(self):
        self._insertCases(100)

        data, gid, sid = {}, '1', '1'

        result = sessionGetLatestCases(data, gid, sid)
        self.assertTrue(result['result'] == 'ok')
        self.assertTrue(len(result['data']['cases']) == 20)

        data = {'amount': 50}
        result = sessionGetLatestCases(data, gid, sid)
        self.assertTrue(result['result'] == 'ok')
        self.assertTrue(len(result['data']['cases']) == 50)       

    def testsessionGetHistoryCases(self):
    	self._insertCases(200)
    	self.db['Sessions'].insert({'gid': 1, 'sid': 1, 'casecount': {'totalnum': 200}})
    	gid, sid = '1', '1'
        data = {'pagenumber': 1, 'pagesize': 20, 'casetype': 'total'}

        result = sessionGetHistoryCases(data, gid, sid)
        self.assertTrue(result['result'] == 'ok')
        self.assertTrue(len(result['data']['cases']) == 20)
        self.assertTrue(result['data']['totalpage'] == 10)

        result = sessionGetHistoryCases({}, gid, sid)
        self.assertTrue(result['result'] == 'ok')
        self.assertTrue(len(result['data']['cases']) == 100)
        self.assertTrue(result['data']['totalpage'] == 2)        

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)