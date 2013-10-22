#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from smartserver.v2.impl.case import *
from pymongo import MongoClient
from smartserver.v2.config import MONGODB_URI
from datetime import datetime 

class TestCase(unittest.TestCase):
    def setUp(self):
        self._mc = MongoClient(MONGODB_URI)
        self.db = self._mc.smartServer_eth

    def _insertCase(self):
        for i in range(1, 10):
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            casename = 'wifi.testOpenWifi_' + str(i)
            self.db['cases'].insert({'tid': i, 'gid': 1, 'sid': 1, 'casename': casename, 'starttime': time})

    def testcaseresultCreate(self):
        gid, sid = '1', '1'
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {'tid': 1, 'casename': 'wifi.testOpenWifi', 'starttime': time}
        result = caseresultCreate(data, gid, sid)
        self.assertTrue(result['result'] == 'ok')
        self.assertTrue(self.db['cases'].find({'casename': 'wifi.testOpenWifi'}).count() == 1)

    def testcaseresultUpdate(self):
        self._insertCase()
        gid, sid = '1', '1'
        data = {'tid': [1,2,3], 'comments': {'issuetype': 'phoneHang', 'caseresult': 'fail'}}
        caseresultUpdate(data, gid, sid)
        self.assertTrue(self.db['cases'].find({'comments.caseresult': 'fail'}).count() == 3)

        data = {'tid': 4, 'result': 'block', 'endtime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'traceinfo': 'test'}
        caseresultUpdate(data, gid, sid)
        self.assertTrue(self.db['cases'].find({'result': 'block'}).count() == 1)

    def testuploadPng(self):
        self._insertCase()
        gid, sid, tid = '1', '1', '1'
        imagedata = open('1.png', 'rb').read()
        stype = 'expect:1.png'

        uploadPng(gid, sid, tid, imagedata, stype)
        self.assertTrue(self.db['cases'].find({'tid': 1})[0]['expectshot'])

    def testuploadZip(self):
        #self._insertCase()
        gid, sid, tid = '1', '1', '1'
        logdata = open('1.zip', 'rb').read()
        xtype = ''

        uploadZip(gid, sid, tid, logdata, xtype)
        self.assertTrue(self.db['cases'].find({'tid': 1})[0]['log'])

    def testtestcaseGetSnapshots(self):
        self._insertCase()
        gid, sid, tid = '1', '1', '1'
        result = testcaseGetSnapshots(gid, sid, tid)
        self.assertTrue(result['result'] == 'error')

    def testtestcaseGetLog(self):
        self._insertCase()
        gid, sid, tid = '1', '1', '1'
        result = testcaseGetLog(gid, sid, tid)
        self.assertTrue(result['result'] == 'error')    	

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)