#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from smartserver.v1.impl.case import *
from pymongo import MongoClient
from smartserver.v1.config import MONGODB_URI
from datetime import datetime 

class TestCase(unittest.TestCase):
    def setUp(self):
        self._mc = MongoClient(MONGODB_URI)
        self.db = self._mc.smartServer_eth

    def _insertCase(self):
        self.db['Sessions'].insert({'gid': 1, 'sid': '1', 'casecount':{'total': 0, 'pass': 0, 'fail': 0, 'block': 0}})
        for i in range(1, 10):
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            casename = 'wifi.testOpenWifi_' + str(i)
            self.db['Cases'].insert({'tid': i, 'gid': 1, 'sid': '1', 'casename': casename, 'starttime': time, 'result': 'running'})

    def testcaseresultCreate(self):
        sid = '1'
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {'tid': 1, 'casename': 'wifi.testOpenWifi', 'starttime': time}
        result = caseresultCreate(data, sid)
        self.assertTrue(result['result'] == 'ok')
        self.assertTrue(self.db['Cases'].find({'casename': 'wifi.testOpenWifi'}).count() == 1)

    def testcaseresultUpdate(self):
        self._insertCase()
        sid = '1'
        data = {'tid': [1,2,3], 'comments': {'issuetype': 'phoneHang', 'caseresult': 'fail'}}
        caseresultUpdate(data, sid)
        self.assertTrue(self.db['Cases'].find({'comments.caseresult': 'fail'}).count() == 3)

        data = {'tid': 4, 'result': 'block', 'endtime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'traceinfo': 'test'}
        caseresultUpdate(data, sid)
        self.assertTrue(self.db['Cases'].find({'result': 'block'}).count() == 1)

    def testuploadPng(self):
        self._insertCase()
        sid, tid = '1', '1'
        imagedata = open('1.png', 'rb').read()
        stype = 'expect:1.png'

        uploadPng(sid, tid, imagedata, stype)
        self.assertTrue(self.db['Cases'].find({'tid': 1})[0]['expectshot'])

    def testuploadZip(self):
        self._insertCase()
        sid, tid = '1', '1'
        logdata = open('1.zip', 'rb').read()
        xtype = ''

        uploadZip(sid, tid, logdata, xtype)
        self.assertTrue(self.db['Cases'].find({'tid': 1})[0]['log']) 	

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)