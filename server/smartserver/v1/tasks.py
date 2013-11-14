#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .worker import worker as w
from .impl import taskimpl
from .impl import sendmail

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
def ws_update_session_sessionsummary(sid, results):
	taskimpl.sessionUpdateSummary(sid, results)

@w.task()
def ws_validate_token_expiretime():
	taskimpl.tokenValidateExpireTime()

@w.task()
def ws_send_activeaccount_mail(recipient, name, token, baseurl):
	sendmail.sendActiveAccountMail(recipient, name, token, baseurl)

@w.task()
def ws_send_retrievepswd_mail(recipient, pswd, baseurl):
	sendmail.sendRetrievePswdMail(recipient, pswd, baseurl)

@w.task()
def ws_send_invitation_mail(recipient, name, orguser, baseurl):
	sendmail.sendInvitationMail(recipient, name, orguser, baseurl)
