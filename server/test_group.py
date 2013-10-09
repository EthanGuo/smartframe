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
        self.db['usetoken'].insert({'appid':'03', 'uid':9, 'token': 'abcdefg'})

    def test_groupCreate(self):
        data = {'token': 'abcdefg', 'groupname': 'test'}
        result = groupCreate(data)
        self.assertTrue(self.db['groups'].find({'gid': result['data']['gid']}).count() == 1)
        self.assertTrue(self.db['groups'].find({'groupname': data['groupname']}).count() == 1)
        result = groupCreate(data)
        self.assertTrue(result['results'] == 'error')

    def __insertGroup(self):
        data = {'groupname': 'test', 'gid': 5, 'members': [{'uid': 0, 'role': 0}, {'uid': 1, 'role': 1}, {'uid': 2, 'role': 2}]}
        self.db['groups'].insert(data)
        self.db['user'].insert({'appid':'03', 'username':'test0', 'uid': 0,'password':'123456', 'info': {'email': 'test0@borqs.com'}})
        self.db['usetoken'].insert({'appid':'03', 'uid':0, 'token': '000000'}) # owner
        self.db['user'].insert({'appid':'03', 'username':'test1', 'uid': 1,'password':'123456', 'info': {'email': 'test1@borqs.com'}})
        self.db['usetoken'].insert({'appid':'03', 'uid':1, 'token': '111111'}) # admin
        self.db['user'].insert({'appid':'03', 'username':'test2', 'uid': 2,'password':'123456', 'info': {'email': 'test2@borqs.com'}})
        self.db['usetoken'].insert({'appid':'03', 'uid':2, 'token': '222222'}) # member
        self.db['usetoken'].insert({'appid':'03', 'uid':3, 'token': '333333'}) # Test token

    def test_groupDelete(self):
        self.__insertGroup()

        data = {'token': '222222', 'gid': 5}
        result = groupDelete(data)
        self.assertTrue(result['results'] == 'error')

        data = {'token': '111111', 'gid': 5}
        result = groupDelete(data)
        self.assertTrue(self.db['groups'].find({'gid': 5}).count() == 0)

    def test_addGroupMembers(self):
        self.__insertGroup()

        data = {'token': '222222', 'members':[{'uid': 3, 'role': 0}]}
        addGroupMembers(data, 5)
        self.assertTrue(len(self.db['groups'].find({'gid': 5})[0]['members']) == 3)

        data = {'token': '000000', 'members':[{'uid': 3, 'role': 0}]}
        addGroupMembers(data, 5)
        self.assertTrue(len(self.db['groups'].find({'gid': 5})[0]['members']) == 4)

    def test_setGroupMembers(self):
        self.__insertGroup()

        data = {'token': '222222', 'members':[{'uid': 2, 'role': 0}]}
        setGroupMembers(data, 5)
        for member in self.db['groups'].find({'gid': 5})[0]['members']:
            if member['uid'] == 2:
                self.assertTrue(member['role'] == 2)

        data = {'token': '000000', 'members':[{'uid': 2, 'role': 0}]}
        setGroupMembers(data, 5)
        for member in self.db['groups'].find({'gid': 5})[0]['members']:
            if member['uid'] == 2:
                self.assertTrue(member['role'] == 0)

    def test_delGroupMembers(self):
        self.__insertGroup()

        data = {'token': '222222', 'members':[{'uid': 2, 'role': 2}]}
        delGroupMembers(data, 5)
        Members = self.db['groups'].find({'gid': 5})[0]['members']
        self.assertTrue(Members[2]['role'] == 2)
        self.assertTrue(Members[2]['uid'] == 2)

        data = {'token': '000000', 'members':[{'uid': 2, 'role': 2}]}
        delGroupMembers(data, 5)
        Members = self.db['groups'].find({'gid': 5})[0]['members']
        self.assertTrue(len(Members) == 2)

    def test_groupGetInfo(self):
        self.__insertGroup()

        data = {'token': '333333'}
        result = groupGetInfo(data, 5)
        self.assertTrue(result['results'] == 'error')

        data = {'token': '222222'}
        result = groupGetInfo(data, 5)
        self.assertTrue(len(result['data']['members']) == 3)

    # def test_groupGetSessionsSummary(self):
    #     pass

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
	unittest.main(verbosity=2)