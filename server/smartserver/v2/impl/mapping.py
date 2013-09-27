#!/usr/bin/env python
# -*- coding: utf-8 -*-

from account import *

func_match = {'register': accountRegister,
            'login': accountLogin,
            'forgotpasswd': accountForgotPasswd,
            #accountWithOutUid
            'changepasswd': accountChangepasswd,
            'update': accountUpdate,
            'invite': accountInvite,
            'logout': accountLogout,
            #accountWithUid
            'info': accountGetInfo,
            'list': accountGetList
            #doAccountGetAction
            }

def accountWithOutUid(data):
    """
       Implement account register/forgotpasswd/login here.
    """
    return func_match.get(data['subc'])(data['data'])

def accountWithUid(data, uid):
    """
       Implement account changepasswd/update/invite/logout here.
    """
    return func_match.get(data['subc'])(uid, data['data'])

def getAccountInfo(data, uid):
    """
       Implement account info/list here.
    """
    return func_match.get(data['subc'])(uid)


# def doGroupBasicAction(data):
#     if data['action'] == 'create':
#         return doGroupCreate(data['data'])
#     elif data['action'] == 'delete':
#         return doGroupDelete(data['data'])

# def doGroupMemeberAction(gid,data):
#     if data['action'] == 'setmember':
#         return setGroupMembers(gid,data['data'])
#     elif data['action'] == 'addmember':
#         return addGroupMembers(gid,data['data'])
#     elif data['action'] == 'delmember':
#         return delGroupMembers(gid,data['data'])

# def doGroupGetAction(gid,data):
#     if data['action'] =='info':
#         return getGroupInfo(gid, data['data'])
#     elif data['action'] == 'testsummary':
#         return getTestSessionSummary(gid, data['data'])

# def doTestSessionBasicAction(gid,sid,data):
#     if data['action'] =='create':
#         return createTestSession(gid,sid,data['data'])
#     elif data['action'] =='update':
#         return updateTestSession(gid,sid,data['data'])
#     elif data['action'] == 'delete':
#         return deleteTestSession(gid,sdi,data['data'])

# def doTestSessionGetAction(gid,sid,data):
#     if data['action'] =='results':
#         return getSessionAllresults(gid,sid,data['data'])
#     elif data['action'] == 'getcase':
#         return getSessionLive(gid,sid,data['data'])
#     elif data['action'] =='summary':
#         return getSessionSummary(gid,sid,data['data'])

# def doTestCaseBasicAction(gid,sid,tid,data):
#     if data['action'] == 'create':
#         return createTestCaseResult(gid,sid,tid,data['data'])
#     elif data['action'] == 'update':
#         return updateTestCaseResult(gid,sid,tid,data['data'])
