#!/usr/bin/env python
# -*- coding: utf-8 -*-

from account import *
from group import *

account_func = {'register': accountRegister,
                'login': accountLogin,
                'forgotpasswd': accountForgotPasswd, #accountWithOutUid
                'changepasswd': accountChangepasswd,
                'update': accountUpdate,
                'invite': accountInvite,
                'logout': accountLogout, #accountWithUid
                'info': accountGetInfo,
                'list': accountGetList, #doAccountGetAction            
            }

group_func = {  'create': groupCreate,
                'delete': groupDelete, #groupBasicAction
                'addmember': addGroupMembers,
                'setmember': setGroupMembers,
                'delmember': delGroupMembers, #groupMemeberAction
                'info': groupGetInfo,
                'sessionsummary': groupGetSessionsSummary, #getGroupInfo
            }

def getUserId(token):
    """
       Used by login plugin to verify the valid of current token
    """
    return accountValidToken(token)

def accountWithOutUid(data):
    """
       Implement account register/forgotpasswd/login here.
    """
    return account_func.get(data['subc'])(data['data'])

def accountWithUid(data, uid):
    """
       Implement account changepasswd/update/invite/logout here.
    """
    return account_func.get(data['subc'])(data['data'], uid)

def getAccountInfo(data, uid):
    """
       Implement account info/list here.
    """
    return account_func.get(data['subc'])(uid)


def groupBasicAction(data, uid):
    """
       Implement group create/delete here.
    """
    return group_func.get(data['subc'])(data['data'], uid)

def groupMemberAction(data, gid, uid):
    """
       Implement group add member/set member role/remove member here.
    """
    return group_func.get(data['subc'])(data['data'], gid, uid)

def getGroupInfo(data, gid, uid):
    """
       Implement group get info/get related session summary here.
    """
    return group_func.get(data['subc'])(gid, uid)


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
