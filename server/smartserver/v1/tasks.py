#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .worker import worker as w
from .impl import taskimpl

@w.task()
def ws_del_session(sid):
	taskimpl.sessionRemoveAll(sid)

@w.task()
def ws_del_group(gid):
    taskimpl.groupRemoveAll(gid)

@w.task()
def ws_del_dirty():
	taskimpl.dirtyDataRemoveAll()

@w.task()
def ws_set_session_endtime(sid):
	taskimpl.sessionSetEndTime(sid)

@w.task()
def ws_active_testsession(sid):
    taskimpl.sessionActiveSession(sid)

@w.task()
def ws_validate_testcase_endtime():
	taskimpl.caseValidateEndtime()

@w.task()
def ws_validate_session_endtime():
	taskimpl.sessionValidateEndtime()

@w.task()
def ws_update_session_domainsummary(sid, results):
    taskimpl.sessionUpdateDomainSummary(sid, results)

@w.task()
def ws_validate_token_expiretime():
	taskimpl.tokenValidateExpireTime()
