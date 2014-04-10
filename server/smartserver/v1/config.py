#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from urlparse import urlparse

__all__ = ["MONGODB_URI", "MONGODB_HOST", "MONGODB_PORT", "WEB_HOST", "WEB_PORT"]

MONGODB_URI = CELERY_BRK_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017").strip()
MONGODB_URI = MONGODB_URI.replace("mongodb://", "")
MONGODB_HOST = MONGODB_URI.split(':')[0]
MONGODB_PORT = int(MONGODB_URI.split(':')[1])
WEB_HOST = os.getenv("WEB_HOST", "")
WEB_PORT = int(os.getenv("WEB_PORT", "80"))
DATA_DB_NAME = 'smartServer'
FILE_DB_NAME = 'smartFile'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
