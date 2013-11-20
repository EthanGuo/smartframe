#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Internal APIs to implement sending invitation/verification email.
'''

import smtplib
from email.MIMEText import MIMEText

SENDER = 'borqsat@borqs.com'
MAILUSER = 'borqsat@borqs.com'
MAILPSWD = '!QAZ2wsx3edc'
SMTP_SERVER = 'smtp.bizmail.yahoo.com'

def __sendMail(receiver,subject,message):
    msg = MIMEText(message,_subtype='plain',_charset='gb2312')      
    msg['Subject'] = subject      
    msg['From'] = SENDER     
    msg['To'] = ';'.join(receiver) 
    smtp = None
    try:
        smtp = smtplib.SMTP_SSL()
        smtp.connect(SMTP_SERVER)
        smtp.login(MAILUSER, MAILPSWD)
        smtp.sendmail(SENDER, receiver, msg.as_string())
    except Exception, e:
        print e
    smtp.quit()

def sendActiveAccountMail(receiver, user, token, baseurl):
    subject = 'Please active your account of SmartAT'
    print 'Sending account activation email to '+receiver

    msg = 'Hi,%s,\r\n\r\n' %(user)
    msg = msg + 'Your account \"%s\" has been created already.\r\n' % (user)
    msg = msg + 'Please verify your email via the url as below within a day.\r\n\r\n'
    msg = msg + baseurl + '/account/active?token=' + token + '\r\n'
    msg = msg + '\r\n\r\n'
    msg = msg + 'Best Regards\r\n'
    msg = msg + 'SmartAT Team\r\n'
    msg = msg + '\r\n\r\n'
    msg = msg + 'This mail is sent out by smartAT, do not reply to it directly.\r\n'

    __sendMail([receiver],subject,msg)

def sendInvitationMail(receiver, user, orguser, baseurl):
    subject = 'Invitation to SmartAT from %s' %(orguser)
    print 'Sending invitation email to ' + receiver

    msg = 'Hi,%s,\r\n\r\n' % (user)
    msg = msg + 'Your friend \"%s\" invite you to join SmartAT.\r\n' %(orguser)
    msg = msg + 'You are welcomed to signup your own account via the url below.\r\n\r\n'
    msg = msg + baseurl.replace('/smartapi', '/smartserver/index.html#/smartserver/signup') + '\r\n'
    msg = msg + '\r\n\r\n'
    msg = msg + 'Best Regards\r\n'
    msg = msg + 'SmartAT Team\r\n'
    msg = msg + '\r\n\r\n'
    msg = msg + 'This mail is sent out by smartAT, do not reply to it directly.\r\n'

    __sendMail([receiver],subject,msg)

def sendRetrievePswdMail(receiver, passwd, baseurl):
    subject = 'Your password to SmartAT has been reset'
    print 'Sending retrieve password email to ' + receiver

    msg = 'Hi,%s,\r\n\r\n' % (receiver)
    msg = msg + 'Your password of account \"%s\" has been reset already.\r\n\r\n' % (receiver)
    msg = msg + 'The new password is ' + passwd + ' \r\n\r\n'
    msg = msg + 'Please login SmartAT and change new one for your own.\r\n'
    msg = msg + '\r\n\r\n'
    msg = msg + 'Best Regards\r\n'
    msg = msg + 'SmartAT Team\r\n'
    msg = msg + '\r\n\r\n'
    msg = msg + 'This mail is sent out by smartAT, do not reply to it directly.\r\n'

    __sendMail([receiver],subject,msg)

def sendErrorMail(context):
    subject='Case Error'

    msg = 'Hi,\r\n\r\n'
    msg = msg + 'This mail sent out by smartAT, do not reply to it directly.\r\n'
    msg = msg + 'Devices '+context['info']['deviceid']+' happen error at '+ context['info']['issuetime']+  '.\r\n' 
    msg = msg + 'Error case name is '+context['info']['testcasename'] +' .\r\n'
    msg = msg + 'This session starts time is '+context['info']['starttime'] +' .\r\n'
    msg = msg + 'please go to http://ats.borqs.com/smartserver/ to checked it, Thanks!\r\n' 
    msg = msg + '\r\n\r\n'
    msg = msg + 'Best Regards\r\n'
    msg = msg + 'SmartAT Team\r\n'

    __sendMail(context['receiver'],subject,msg)