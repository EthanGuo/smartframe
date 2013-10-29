#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .worker import worker as w
from .impl import session, account, case

# @w.task(ignore_result=True)
# def ws_del_session(sid):
#     '''
#     Delete FS according to the sid by using worker task
#     '''
#     store.del_session(sid)


# @w.task(ignore_result=True)
# def ws_del_group(gid):
#     '''
#     Delete FS and results according to gid by using worker task
#     '''
#     store.del_group(gid)


# @w.task(ignore_result=True)
# def ws_del_dirty():
#     '''
#     Scheduled task to clear dirty FS.
#     '''
#     store.del_dirty()


# @w.task(ignore_result=True)
# def ws_check_fs(fid):
#     store.check_fs(fid)


@w.task(ignore_result=True)
def ws_set_session_endtime(sid):
	session.sessionSetEndTime(sid)

@w.task(ignore_result=True)
def ws_active_testsession(sid):
    session.sessionActiveSession(sid)

@w.task(ignore_result=True)
def ws_validate_testcase_endtime():
	case.caseValidateEndtime()

@w.task(ignore_result=True)
def ws_update_session_domainsummary(sid, results, status):
    session.sessionUpdateDomainSummary(sid, results, status)

@w.task(ignore_result=True)
def ws_validate_token_expiretime():
	account.tokenValidateExpireTime()
