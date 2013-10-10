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
        url = 'http://127.0.0.1:8080/smartserver/group'
        headers = {'content-type': 'application/json'}

        createData = {'subc': 'create', 'data': {'token': 'abcdefg', 'groupname': 'test'}}
        result = requests.post(url=url, data=json.dumps(createData), headers=headers)
        self.assertTrue(result['results'] == 'ok')


    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)