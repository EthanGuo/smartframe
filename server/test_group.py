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
        self.db['user'].insert({'appid':'03', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})

    def test_groupCreate(self):
        data = {'groupname': 'test'}
        result = groupCreate(data, 9)
        self.assertTrue(self.db['groups'].find({'gid': result['data']['gid']}).count() == 1)
        self.assertTrue(self.db['groups'].find({'groupname': data['groupname']}).count() == 1)
        result = groupCreate(data, 9)
        self.assertTrue(result['results'] == 'error')

    def __insertGroup(self):
        data = {'groupname': 'test', 'gid': 5, 'members': [{'uid': 0, 'role': 0}, {'uid': 1, 'role': 1}, {'uid': 2, 'role': 2}]}
        self.db['groups'].insert(data)
        self.db['user'].insert({'appid':'03', 'username':'test0', 'uid': 0,'password':'123456', 'info': {'email': 'test0@borqs.com'}})# owner
        self.db['user'].insert({'appid':'03', 'username':'test1', 'uid': 1,'password':'123456', 'info': {'email': 'test1@borqs.com'}})# admin
        self.db['user'].insert({'appid':'03', 'username':'test2', 'uid': 2,'password':'123456', 'info': {'email': 'test2@borqs.com'}})# member
        self.db['user'].insert({'appid':'03', 'username':'test3', 'uid': 3,'password':'123456', 'info': {'email': 'test3@borqs.com'}}) # Test token

    def test_groupDelete(self):
        self.__insertGroup()

        data = {'gid': 5}
        result = groupDelete(data, 2)
        self.assertTrue(result['results'] == 'error')

        data = {'gid': 5}
        result = groupDelete(data, 1)
        self.assertTrue(self.db['groups'].find({'gid': 5}).count() == 0)

    def test_addGroupMembers(self):
        self.__insertGroup()

        data = {'members':[{'uid': 3, 'role': 0}]}
        addGroupMembers(data, 5, 2)
        self.assertTrue(len(self.db['groups'].find({'gid': 5})[0]['members']) == 3)

        data = {'members':[{'uid': 3, 'role': 0}]}
        addGroupMembers(data, 5, 0)
        self.assertTrue(len(self.db['groups'].find({'gid': 5})[0]['members']) == 4)

    def test_setGroupMembers(self):
        self.__insertGroup()

        data = {'members':[{'uid': 2, 'role': 0}]}
        setGroupMembers(data, 5, 2)
        for member in self.db['groups'].find({'gid': 5})[0]['members']:
            if member['uid'] == 2:
                self.assertTrue(member['role'] == 2)

        data = {'members':[{'uid': 2, 'role': 0}]}
        setGroupMembers(data, 5, 0)
        for member in self.db['groups'].find({'gid': 5})[0]['members']:
            if member['uid'] == 2:
                self.assertTrue(member['role'] == 0)

    def test_delGroupMembers(self):
        self.__insertGroup()

        data = {'members':[{'uid': 2, 'role': 2}]}
        delGroupMembers(data, 5, 2)
        Members = self.db['groups'].find({'gid': 5})[0]['members']
        self.assertTrue(Members[2]['role'] == 2)
        self.assertTrue(Members[2]['uid'] == 2)

        data = {'members':[{'uid': 2, 'role': 2}]}
        delGroupMembers(data, 5, 0)
        Members = self.db['groups'].find({'gid': 5})[0]['members']
        self.assertTrue(len(Members) == 2)

    def test_groupGetInfo(self):
        self.__insertGroup()

        result = groupGetInfo(5, 3)
        self.assertTrue(result['results'] == 'error')

        result = groupGetInfo(5, 2)
        self.assertTrue(len(result['data']['members']) == 3)

    # def test_groupGetSessionsSummary(self):
    #     pass

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
	unittest.main(verbosity=2)