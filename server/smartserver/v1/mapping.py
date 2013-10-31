#!/usr/bin/env python
# -*- coding: utf-8 -*-

from impl.account import *
from impl.group import *
from impl.case import *
from impl.session import *
from impl.filedealer import *

account_func = {'register': accountRegister,
                'login': accountLogin,
                'retrievepswd': accountRetrievePasswd, #accountBasic
                'changepswd': accountChangepasswd,
                'update': accountUpdate,
                'invite': accountInvite,
                'logout': accountLogout, #accountPOST
                'accountlist': accountGetUserList,                 
                'accountinfo': accountGetInfo,
                'groups': accountGetGroups,
                'sessions': accountGetSessions,#accountGet           
            }

group_func = {  'create': groupCreate, #groupBasic
                'delete': groupDelete, 
                'setmember': groupSetMembers,
                'delmember': groupDelMembers, #groupPOST
                'members': groupGetMembers,
                'sessions': groupGetSessions,
                'cycles': groupGetCycles,
                'report': groupGetReport,#groupGET
            }

session_func ={ 'create': sessionCreate,
                'update':sessionUpdate,
                'cycle': sessionCycle,
                'delete':sessionDelete, #sessionPOST
                'summary':sessionSummary,
                'poll':sessionPollStatus,
                'latest':sessionGetLatestCases,
                'history': sessionGetHistoryCases, #sessionGET
            }

case_func = {   'create':caseresultCreate,
                'update':caseresultUpdate, #casePOST
            }

caseupload_func = {'uploadpng': uploadPng,
                   'uploadzip': uploadZip, #caseFilePUT
            }

def getUserId(token):
    """
       Used by login plugin to verify the valid of current token
    """
    return accountValidToken(token)

def filePUT(content_type, filedata):
    """
       Used to upload file and upload file only
    """
    return saveFile(filedata, content_type)

def fileGET(fileid):
    """
       Used to get the image/log data of testcase. 
    """
    return fetchFileData(fileid)

def uploadSessionResult(filedata, gid, sid):
    """
       Used to upload xml containing case result of a session
    """
    return sessionUploadXML(filedata, gid, sid)

def accountActive(uid):
    """
       Used to active user account
    """
    return accountActiveUser(uid)

def accountBasic(data):
    """
       Implement account register/retrievepswd/login here.
    """
    return account_func.get(data['subc'])(data['data'])

def accountPOST(data, uid):
    """
       Implement account changepswd/update/invite/logout here.
    """
    return account_func.get(data['subc'])(data['data'], uid)

def accountGet(data, uid):
    """
       Implement account get user list/user info/joined groups/started sessions here.
    """
    return account_func.get(data['subc'])(uid)


def groupBasic(data, uid):
    """
       Implement group create here.
    """
    return group_func.get(data['subc'])(data['data'], uid)

def groupPOST(data, gid, uid):
    """
       Implement group delete/(add/set) (member/role)/remove member here.
    """
    return group_func.get(data['subc'])(data['data'], gid, uid)

def groupGet(data, gid, uid):
    """
       Implement group get info/get related session summary/get report here.
    """
    return group_func.get(data['subc'])(data['cid'], gid, uid)

def sessionPOST(data, gid, sid, uid):
    """
    Implement session create/update/cycle/delete.
    """
    return session_func.get(data['subc'])(data['data'], gid, sid, uid)

def sessionGET(data, gid, sid):
    """
    Implement get session summary
    """
    return session_func.get(data['subc'])(data['data'], gid, sid)

def casePOST(data, sid):
    """
    Implement case results create/update.
    """
    return case_func.get(data['subc'])(data['data'], gid, sid)

def caseFilePUT(subc, sid, tid, data, xtype):
    """
    Implement case log, snapshot upload.
    """
    return caseupload_func.get(subc)(sid, tid, data, xtype)
