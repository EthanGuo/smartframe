#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smartserver.v2.impl.account import *
from smartserver.v2.config import MONGODB_URI
from pymongo import MongoClient
import unittest

class TestAccount(unittest.TestCase):
    def setUp(self):
        self._mc = MongoClient(MONGODB_URI)
        self.db = self._mc.smartServer_eth

    def test_createToken(self):
        token = createToken('03', 9)
        self.assertTrue(self.db['usetoken'].find({'token': token}).count() == 1)

    def test_accountRegister(self):
        data = {'username': 'test', 'password': '123456', 'tokenType': '03', 'info': {'email': 'test@borqs.com'}}
        token = accountRegister(data)['data']['token']
        self.assertTrue(self.db['user'].find({'username': 'test', 'tokenType': '03', 'info.email': 'test@borqs.com'}).count())
        self.assertTrue(self.db['usetoken'].find({'token': token}).count())

        result = accountRegister(data)
        self.assertTrue(result['results'] == 'error')

        data = {'username': 'test', 'password': '123456', 'tokenType': '03', 'info': {'email': 'test1@borqs.com'}}
        result = accountRegister(data)
        self.assertTrue(result['results'] == 'error')

        data = {'username': 'test1', 'password': '123456', 'tokenType': '03', 'info': {'email': 'test@borqs.com'}}
        result = accountRegister(data)
        self.assertTrue(result['results'] == 'error') 

    def test_accountLogin(self):
        self.db['user'].insert({'tokenType':'03', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})

        dataUsername = {'tokenType':'03', 'username':'test', 'password':'123456'}
        result = accountLogin(dataUsername)
        self.assertTrue(self.db['usetoken'].find(result['data']).count() == 1)
        self.db['usetoken'].remove({'token': result['data']['token']})

        dataEmail = {'tokenType':'03', 'username':'test@borqs.com', 'password':'123456'}
        result = accountLogin(dataEmail)
        self.assertTrue(self.db['usetoken'].find(result['data']).count() == 1)
        self.db['usetoken'].remove({'token': result['data']['token']})

        dataWrongUsername = {'tokenType':'03', 'username':'test1', 'password':'123456'}
        result = accountLogin(dataWrongUsername)
        self.assertTrue(result['results'] == 'error')

    def test_accountForgotPasswd(self):
        self.db['user'].insert({'tokenType':'03', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})

        result = accountForgotPasswd({'email': 'test@borqs.com'})
        self.assertTrue(result['results'] == 'ok')

        result = accountForgotPasswd({'email': 'test1@borqs.com'})
        self.assertTrue(result['results'] == 'error')

    def test_accountChangepasswd(self):
        data = {'tokenType':'03', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}}
        self.db['user'].insert(data)

        uid = 9
        data = {'newpassword': '654321', 'oldpassword': '123456'}
        result = accountChangepasswd(uid, data)
        self.assertTrue(result['results'] == 'ok')

        data = {'newpassword': '654321', 'oldpassword': '12345'}
        result = accountChangepasswd(uid, data)
        self.assertTrue(result['results'] == 'error')

    def test_accountLogout(self):
        token = createToken('03', 9)

        data = {'token': token}
        accountLogout(9, data)
        self.assertFalse(self.db['usetoken'].find({'token': token}).count())

    def test_accountGetInfo(self):
        self.db['user'].insert({'tokenType':'03', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}})
        
        result = accountGetInfo(9)
        self.assertTrue(self.db['user'].find({'uid': result['data']['uid']}).count() == 1)
        self.assertTrue(self.db['user'].find({'username': result['data']['username']}).count() == 1)

        result = accountGetInfo(8)
        self.assertTrue(result['results'] == 'error')

    def test_accountGetList(self):
        self.db['user'].insert({'tokenType':'03', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}})
        
        result = accountGetList(9)
        for user in result['data']['users']:
            self.assertTrue(self.db['user'].find({'uid': user['uid'], 'username': user['username']}).count() == 1)

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)
