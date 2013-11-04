#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smartserver.v1.impl.filedealer import *
import unittest
from pymongo import MongoClient
from smartserver.v1.config import MONGODB_URI

class TestFileDealer(unittest.TestCase):
    def setUp(self):
        self._mc = MongoClient(MONGODB_URI)
        self.db = self._mc.smartServer_eth

    def testfiledealer(self):
        filedata = open('1.png', 'rb').read()
        content_type = 'image/png'
        filename = '1.png'

        fileid = saveFile(filedata, content_type, filename).strip().replace('/file/', '')
        self.assertTrue(self.db['Files'].find({'fileid': fileid}))

        result = fetchFileData(fileid)
        self.assertTrue(result['data']['filename'] == '1.png')
        self.assertTrue(result['data']['content_type'] == 'image/png')

        deleteFile(fileid)
        self.assertFalse(self.db['Files'].find({'fileid': fileid}).count())

    def tearDown(self):
        self._mc.drop_database('smartServer_eth')

if __name__ == '__main__':
    unittest.main(verbosity=2)