#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db import Files, File
import uuid, hashlib
from util import resultWrapper

def generateUniqueID():
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    return m.hexdigest()

def saveFile(filedata, content_type, filename=''):
    fileid = generateUniqueID()
    new = File()
    new.data.new_file()
    new.data.write(filedata)
    new.data.close()
    newfile = Files(fileid=fileid, filename=filename, filedata=new, content_type=content_type)
    newfile.save()
    return fileid

def fetchFileData(fileid):
    """
    params, data: {'fileid':(string)fileid}
    return, data: {'filedata':(bytes)filedata, 'filename': (string)filename, 'content_type': (string)type}
    """
    #If fileid is valid, return filedata, or return error
    targetfile = Files.objects(fileid=fileid).first()
    if targetfile:
        filedata = targetfile.filedata.data.read()
        filename = targetfile.filename
        content_type = targetfile.content_type
        return resultWrapper('ok', {'filedata': filedata, 'filename': filename, 'content_type': content_type}, '')
    else:
        return resultWrapper('error', {}, 'Invalid ID!')