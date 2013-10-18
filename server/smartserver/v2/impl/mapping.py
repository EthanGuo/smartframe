#!/usr/bin/env python
# -*- coding: utf-8 -*-

from account import *
from group import *
from case import *

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
                'sessionsummary': groupGetSessionsSummary, 
                'cyclereport': groupGetCycleReport,#getGroupInfo
            }

session_func ={ 'create':sessionCreate,
                'update':sessionUpdate,
                'delete':sessionDelete, #doTestSessionBasicAction
                'summary':sessionsummary,
                'update':sessionupdate,
                'live':sessionlive,
                'history': sessionhistory, #getSessionAction
            }

case_func = {   'create':caseresultCreate,
                'update':caseresultUpdate, #caseResultAction
            }

caseupload_func = {'uploadpng': uploadPng,
                   'uploadzip': uploadZip, #uploadCaseResultFile
            }

def getUserId(token):
    """
       Used by login plugin to verify the valid of current token
    """
    return accountValidToken(token)

def getTestCaseSnaps(gid, sid, tid):
    """
       Used to get the snapshots of testcases.
    """
    return testcaseGetSnapshots(gid, sid, tid)

def getTestCaseLog(gid, sid, tid):
    """
       Used to get the log of testcases.
    """
    return testcaseGetLog(gid, sid, tid)

def getSnapData(imageid):
    """
       Used to get the image data of testcase. 
    """
    return testcaseGetSnapData(imageid)

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
       Implement group get info/get related session summary/get report here.
    """
    return group_func.get(data['subc'])(data['cid'], gid, uid)

def doTestSessionBasicAction(data, gid, sid, uid):
    """
    Implement session create/update/delete.
    """
    return session_func.get(data['subc'])(data['data'], gid, sid, uid)

def getSessionAction(data, gid, sid):
    """
    Implement get session summary
    """
    return session_func.get(data['subc'])(data['data'], gid, sid)

def caseResultAction(data, gid, sid):
    """
    Implement case results create/update.
    """
    return case_func.get(data['subc'])(data['data'], gid, sid)

def uploadCaseResultFile(subc, gid, sid, tid, data, xtype):
    """
    Implement case log, snapshot upload.
    """
    return caseupload_func.get(subc)(gid, sid, tid, data, xtype)
