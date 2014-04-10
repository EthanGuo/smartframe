#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import config
from celery.schedules import crontab

# Included Taskes
CELERY_INCLUDE = ['smartserver.v1.tasks']
# Task Broker
# BROKER_URL = config.REDIS_URI
# Task Result backend
# CELERY_RESULT_BACKEND = config.REDIS_URI
BROKER_URL = config.CELERY_BRK_URI
CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": config.MONGODB_HOST,
    "port": config.MONGODB_PORT
}
CELERY_TASK_RESULT_EXPIRES = 3600

# Scheduled tasks
CELERYBEAT_SCHEDULE = {
    'cleardirty-every-month': {
        'task': 'smartserver.v1.tasks.ws_del_dirty',
        'schedule': crontab(minute=0, hour=0, day_of_month=1)
    },
    'validate-testcase-endtime-every-hour': {
        'task': 'smartserver.v1.tasks.ws_validate_testcase_endtime',
        'schedule': crontab(minute=0, hour='*/1')
    },
    'validate-session-endtime-every-5-mins':{
        'task': 'smartserver.v1.tasks.ws_validate_session_endtime',
        'schedule': crontab(minute='*/5')
    },
    'validate-token-expiretime-every-midnight': {
        'task': 'smartserver.v1.tasks.ws_validate_token_expiretime',
        'schedule': crontab(minute=0, hour=0)
    },
}

CELERY_TIMEZONE = 'Asia/Shanghai'
