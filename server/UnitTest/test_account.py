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

    def testcreateToken(self):
        token = createToken('03', 9)['token']
        self.assertTrue(self.db['usetoken'].find({'token': token}).count() == 1)

    def testaccountRegister(self):
        data = {'username': 'test', 'password': '123456', 'appid': '03', 'info': {'email': 'test@borqs.com'}}
        token = accountRegister(data)['data']['token']
        self.assertTrue(self.db['user'].find({'username': 'test', 'appid': '03', 'info.email': 'test@borqs.com'}).count())
        self.assertTrue(self.db['usetoken'].find({'token': token}).count())

        result = accountRegister(data)
        self.assertTrue(result['result'] == 'error')

        data = {'username': 'test', 'password': '123456', 'appid': '03', 'info': {'email': 'test1@borqs.com'}}
        result = accountRegister(data)
        self.assertTrue(result['result'] == 'error')

        data = {'username': 'test1', 'password': '123456', 'appid': '03', 'info': {'email': 'test@borqs.com'}}
        result = accountRegister(data)
        self.assertTrue(result['result'] == 'error') 

    def testaccountLogin(self):
        self.db['user'].insert({'appid':'03', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})

        dataUsername = {'appid':'03', 'username':'test', 'password':'123456'}
        result = accountLogin(dataUsername)
        self.assertTrue(self.db['usetoken'].find(result['data']).count() == 1)
        self.db['usetoken'].remove({'token': result['data']['token']})

        dataEmail = {'appid':'03', 'username':'test@borqs.com', 'password':'123456'}
        result = accountLogin(dataEmail)
        self.assertTrue(self.db['usetoken'].find(result['data']).count() == 1)
        self.db['usetoken'].remove({'token': result['data']['token']})

        dataWrongUsername = {'appid':'03', 'username':'test1', 'password':'123456'}
        result = accountLogin(dataWrongUsername)
        self.assertTrue(result['result'] == 'error')

    def testaccountForgotPasswd(self):
        self.db['user'].insert({'appid':'03', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})

        result = accountForgotPasswd({'email': 'test@borqs.com'})
        self.assertTrue(result['result'] == 'ok')

        result = accountForgotPasswd({'email': 'test1@borqs.com'})
        self.assertTrue(result['result'] == 'error')

    def testaccountChangepasswd(self):
        data = {'appid':'03', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}}
        self.db['user'].insert(data)

        uid = 9
        data = {'newpassword': '654321', 'oldpassword': '123456'}
        result = accountChangepasswd(data, uid)
        self.assertTrue(result['result'] == 'ok')

        data = {'newpassword': '654321', 'oldpassword': '12345'}
        result = accountChangepasswd(data, uid)
        self.assertTrue(result['result'] == 'error')

    def testaccountLogout(self):
        token = createToken('03', 9)

        data = {'token': token}
        accountLogout(data, 9)
        self.assertFalse(self.db['usetoken'].find({'token': token}).count())

    def testaccountGetInfo(self):
        self.db['user'].insert({'appid':'03', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}})
        
        result = accountGetInfo(9)
        self.assertTrue(self.db['user'].find({'uid': result['data']['userinfo']['uid']}).count() == 1)
        self.assertTrue(self.db['user'].find({'username': result['data']['userinfo']['username']}).count() == 1)

        result = accountGetInfo(8)
        self.assertTrue(result['result'] == 'error')

    def testaccountGetList(self):
        self.db['user'].insert({'appid':'03', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}})
        
        result = accountGetList(9)
        for user in result['data']['users']:
            self.assertTrue(self.db['user'].find({'uid': user['uid'], 'username': user['username']}).count() == 1)

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)
