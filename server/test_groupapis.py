#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pymongo import MongoClient
from smartserver.v2.config import MONGODB_URI
import requests, json

class TestGroupAPIs(unittest.TestCase):
    def setUp(self):
        self._mc = MongoClient(MONGODB_URI)
        self.db = self._mc.smartServer_eth
        self.db['user'].insert({'appid':'03', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})
        self.db['usetoken'].insert({'appid':'03', 'uid':9, 'token': 'abcdefg'})

    def test_doGroupAction(self):
        url = 'http://127.0.0.1:8080/smartapi/group'
        headers = {'content-type': 'application/json'}

        createData = {'subc': 'create', 'data': {'groupname': 'test'}}
        createData['token'] = 'abcdefg'
        result = requests.post(url=url, data=json.dumps(createData), headers=headers)
        result = json.loads(result.content)
        self.assertTrue(result['results'] == 'ok')

        deleteData = {'subc': 'delete', 'data': {'gid': result['data']['gid']}}
        deleteData['token'] = 'abcdefg'
        result = requests.post(url=url, data=json.dumps(deleteData), headers=headers)
        result = json.loads(result.content)
        self.assertTrue(result['results'] == 'ok')

    def test_doMemberToGroupAction(self):
        self.db['groups'].insert({'groupname': 'test', 'gid': 1, 'members': [{'uid': 9, 'role': 0}]})
        url = 'http://127.0.0.1:8080/smartapi/group/1/member'
        headers = {'content-type': 'application/json'}
        
        addData = {"subc": "addmember", "data": {"members": [{"uid": 2, "role": 2}]}}
        addData['token'] = "abcdefg"
        result = requests.post(url=url, data=json.dumps(addData), headers=headers)
        result = json.loads(result.content)
        self.assertTrue(result['results'] == 'ok')
        
        setData = {'subc': 'setmember', 'data': {'members': [{'uid': 2, 'role': 1}]}}
        setData['token'] = 'abcdefg'
        result = requests.post(url=url, data=json.dumps(setData), headers=headers)
        result = json.loads(result.content)
        self.assertTrue(result['results'] == 'ok')

        delData = {'subc': 'delmember', 'data': {'token': 'abcdefg', 'members': [{'uid': 2, 'role': 1}]}}
        delData['token'] = 'abcdefg'
        result = requests.post(url=url, data=json.dumps(delData), headers=headers)
        result = json.loads(result.content)
        self.assertTrue(result['results'] == 'ok')

    def test_doGetGroupInfo(self):
        data = {'groupname': 'test', 'gid': 1, 'members': [{'uid': 0, 'role': 0}, {'uid': 1, 'role': 1}, {'uid': 2, 'role': 2}]}
        self.db['groups'].insert(data)
        self.db['user'].insert({'appid':'03', 'username':'test0', 'uid': 0,'password':'123456', 'info': {'email': 'test0@borqs.com'}})
        self.db['user'].insert({'appid':'03', 'username':'test1', 'uid': 1,'password':'123456', 'info': {'email': 'test1@borqs.com'}})
        self.db['user'].insert({'appid':'03', 'username':'test2', 'uid': 2,'password':'123456', 'info': {'email': 'test2@borqs.com'}})
        self.db['usetoken'].insert({'appid':'03', 'uid':2, 'token': '222222'})
        url = 'http://127.0.0.1:8080/smartapi/group/1/info'

        infoData = {'subc': 'info'}
        infoData['token'] = '222222'

        s = requests.Session()
        prequest = requests.Request("GET", url=url, params=infoData).prepare()
        resp = s.send(prequest)
        self.assertTrue(json.loads(resp.content)['results'] == 'ok')

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)