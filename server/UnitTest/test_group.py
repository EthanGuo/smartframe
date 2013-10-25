#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smartserver.v2.impl.group import *
from smartserver.v2.config import MONGODB_URI
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

        data = {'gid': 5}
        result = groupDelete(data, 2)
        self.assertTrue(result['result'] == 'error')

        data = {'gid': 5}
        result = groupDelete(data, 0)
        self.assertTrue(self.db['Groups'].find({'gid': 5}).count() == 0)

    def testsetGroupMembers(self):
        self.__insertGroup()

        data = {'members':[{'uid': 2, 'role': 10}]}
        setGroupMembers(data, 5, 2)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2})[0]['role'] == 8)

        data = {'members':[{'uid': 2, 'role': 9}]}
        setGroupMembers(data, 5, 0)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2})[0]['role'] == 9)

    def testdelGroupMembers(self):
        self.__insertGroup()

        data = {'members':[{'uid': 2, 'role': 8}]}
        delGroupMembers(data, 5, 2)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2}).count() == 1)

        data = {'members':[{'uid': 2, 'role': 8}]}
        delGroupMembers(data, 5, 0)
        self.assertTrue(self.db['GroupMembers'].find({'gid': 5, 'uid': 2}).count() == 0)

    def testgroupGetInfo(self):
        self.__insertGroup()

        result = groupGetInfo({}, 5, 2)
        self.assertTrue(len(result['data']['members']) == 3)

    def test_groupGetSessionsSummary(self):
        pass

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
	unittest.main(verbosity=2)