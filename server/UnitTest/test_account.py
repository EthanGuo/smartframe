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
        token = createToken('02', 9)['token']
        self.assertTrue(self.db['UserTokens'].find({'token': token}).count() == 1)

    def testaccountRegister(self):
        data = {'username': 'test', 'password': '123456', 'appid': '02', 'info': {'email': 'test@borqs.com'}}
        result =accountRegister(data)
        token = result['data']['token']
        self.assertTrue(self.db['Users'].find({'username': 'test', 'appid': '02', 'info.email': 'test@borqs.com'}).count())
        self.assertTrue(self.db['UserTokens'].find({'token': token}).count())

        result = accountRegister(data)
        self.assertTrue(result['result'] == 'error')

        data = {'username': 'test', 'password': '123456', 'appid': '02', 'info': {'email': 'test1@borqs.com'}}
        result = accountRegister(data)
        self.assertTrue(result['result'] == 'error')

        data = {'username': 'test1', 'password': '123456', 'appid': '02', 'info': {'email': 'test@borqs.com'}}
        result = accountRegister(data)
        self.assertTrue(result['result'] == 'error') 

    def testaccountLogin(self):
        self.db['Users'].insert({'appid':'02', 'username':'test', 'uid': 9,'password':'123456', 'active': True , 'info': {'email': 'test@borqs.com'}})

        dataUsername = {'appid':'02', 'username':'test', 'password':'123456'}
        result = accountLogin(dataUsername)
        self.assertTrue(self.db['UserTokens'].find(result['data']).count() == 1)
        self.db['UserTokens'].remove({'token': result['data']['token']})

        dataEmail = {'appid':'02', 'username':'test@borqs.com', 'password':'123456'}
        result = accountLogin(dataEmail)
        self.assertTrue(self.db['UserTokens'].find(result['data']).count() == 1)
        self.db['UserTokens'].remove({'token': result['data']['token']})

        dataWrongUsername = {'appid':'02', 'username':'test1', 'password':'123456'}
        result = accountLogin(dataWrongUsername)
        self.assertTrue(result['result'] == 'error')

    def testaccountRetrievePasswd(self):
        self.db['Users'].insert({'appid':'02', 'username':'test', 'uid': 9,'password':'123456', 'info': {'email': 'test@borqs.com'}})

        result = accountRetrievePasswd({'email': 'test@borqs.com'})
        self.assertTrue(result['result'] == 'ok')

        result = accountRetrievePasswd({'email': 'test1@borqs.com'})
        self.assertTrue(result['result'] == 'error')

    def testaccountChangepasswd(self):
        data = {'appid':'02', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}}
        self.db['Users'].insert(data)

        uid = 9
        data = {'newpassword': '654321', 'oldpassword': '123456'}
        result = accountChangepasswd(data, uid)
        self.assertTrue(result['result'] == 'ok')

        data = {'newpassword': '654321', 'oldpassword': '12345'}
        result = accountChangepasswd(data, uid)
        self.assertTrue(result['result'] == 'error')

    def testaccountLogout(self):
        token = createToken('02', 9)

        data = {'token': token}
        accountLogout(data, 9)
        self.assertFalse(self.db['UserTokens'].find({'token': token}).count())

    def testaccountGetInfo(self):
        self.db['Users'].insert({'appid':'02', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}})
        
        result = accountGetInfo(9)
        self.assertTrue(self.db['Users'].find({'uid': result['data']['userinfo']['uid']}).count() == 1)
        self.assertTrue(self.db['Users'].find({'username': result['data']['userinfo']['username']}).count() == 1)

        result = accountGetInfo(8)
        self.assertTrue(result['result'] == 'error')

    def testaccountGetUserList(self):
        self.db['Users'].insert({'appid':'02', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}})
        
        result = accountGetUserList(9)
        for user in result['data']['users']:
            self.assertTrue(self.db['Users'].find({'uid': user['uid'], 'username': user['username']}).count() == 1)
    
    def testaccountUpdate(self):
        self.db['Users'].insert({'appid':'02', 'username':'test', 'uid': 9, 'password':'123456', 'info': {'email': 'test@borqs.com'}})
        
        uid = 9
        data = {'file': {'filename': '1.png', 'file': open('1.png','rb').read()}}
        result = accountUpdate(data, uid)
        self.assertTrue(result['result'] == 'ok')

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == "__main__":
    unittest.main(verbosity=2)
