#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smartserver.v1.impl.group import *
from smartserver.v1.config import MONGODB_URI
from pymongo import MongoClient
import unittest

class TestGroup(unittest.TestCase):
    def setUp(self):
        self._mc = MongoClient(MONGODB_URI)
        self.db = self._mc.smartServer_eth
        self.db['Users'].insert({'appid':'02', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})

    def testgroupCreate(self):
        data = {'groupname': 'test'}
        result = groupCreate(data, 9)
        self.assertTrue(self.db['Groups'].find({'gid': result['data']['gid']}).count() == 1)
        self.assertTrue(self.db['Groups'].find({'groupname': data['groupname']}).count() == 1)
        result = groupCreate(data, 9)
        self.assertTrue(result['result'] == 'error')

    def __insertGroup(self):
        data = {'groupname': 'test', 'gid': 5}
        members = [{'uid': 0, 'role': 10, 'gid': 5}, {'uid': 1, 'role': 9, 'gid': 5}, {'uid': 2, 'role': 8, 'gid': 5}]
        self.db['Groups'].insert(data)
        for member in members:
            self.db['GroupMembers'].insert(member)
        self.db['Users'].insert({'appid':'02', 'username':'test0', 'uid': 0,'password':'123456', 'info': {'email': 'test0@borqs.com'}})# owner
        self.db['Users'].insert({'appid':'02', 'username':'test1', 'uid': 1,'password':'123456', 'info': {'email': 'test1@borqs.com'}})# admin
        self.db['Users'].insert({'appid':'02', 'username':'test2', 'uid': 2,'password':'123456', 'info': {'email': 'test2@borqs.com'}})# member
        self.db['Users'].insert({'appid':'02', 'username':'test3', 'uid': 3,'password':'123456', 'info': {'email': 'test3@borqs.com'}}) # Test token

    def testgroupDelete(self):
        self.__insertGroup()

        data = {}
        result = groupDelete(data, 5, 2)
        self.assertTrue(result['result'] == 'error')

        data = {}
        result = groupDelete(data, 5, 0)
        self.assertTrue(self.db['Groups'].find({'gid': 5}).count() == 0)

    def testgroupSetMembers(self):
        self.__insertGroup()

        data = {'members':[{'uid': 2, 'role': 10}]}
        groupSetMembers(data, 5, 2)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2})[0]['role'] == 8)

        data = {'members':[{'uid': 2, 'role': 9}]}
        groupSetMembers(data, 5, 0)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2})[0]['role'] == 9)

    def testgroupDelMembers(self):
        self.__insertGroup()

        data = {'members':[{'uid': 2, 'role': 8}]}
        groupDelMembers(data, 5, 2)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2}).count() == 1)

        data = {'members':[{'uid': 2, 'role': 8}]}
        groupDelMembers(data, 5, 0)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2}).count() == 0)

    def testgroupGetMembers(self):
        self.__insertGroup()

        result = groupGetMembers({}, 5, 2)
        self.assertTrue(len(result['data']['members']) == 3)

    def testgroupGetSessions(self):
        self.db['Groups'].insert({'groupname': 'test', 'gid': 1})
        for i in range(1, 10):
            self.db['Users'].insert({'username': 'test_' + str(i), 'password': '123456', 'uid': i, 'info':{'email': 'test@borqs.com'}})
            self.db['Sessions'].insert({'gid': 1, 'sid': i, 'uid': i})
        result = groupGetSessions({}, '1', 1)
        self.asserTrue(len(result['data']['sessions']) == 9)

    def testgroupGetCycles(self):
        self.db['Groups'].insert({'groupname': 'test', 'gid': 1})
        for i in range(1, 10):
            self.db['Sessions'].insert({'gid': 1, 'sid': i, 'deviceinfo':{'product': 'BKB', 'revision': 'abcd'}})
        self.db['Cycles'].insert({'gid': 1, 'sids':[1,2,3,4], 'cid': 1})
        self.db['Cycles'].insert({'gid': 1, 'sids':[5,6,7,8], 'cid': 2})
        self.db['Cycles'].insert({'gid': 1, 'sids':[9], 'cid': 3})

        result = groupGetCycles({}, '1', 1)
        self.assertTrue(len(result['data']['cycles']) == 3)

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
	unittest.main(verbosity=2)