#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db import Files, File
import uuid, hashlib
from mongoengine import OperationError
from util import resultWrapper

def generateUniqueID():
    m = hashlib.md5()
    m.update(str(uuid.uuid1()))
    return m.hexdigest()

def saveFile(filedata, content_type, filename=''):
    """
    params, data: {'filedata':(bytes), 'content_type':(string), 'filename':(string)}
    return, data: url to fetch file
    """
    fileid = generateUniqueID()
    new = File()
    new.data.new_file()
    new.data.write(filedata)
    new.data.close()
    newfile = Files(fileid=fileid, filename=filename, filedata=new, content_type=content_type)
    try:
        newfile.save()
    except OperationError:
        newfile.save()
    return {'url':'/file/' + fileid, 'filename': filename}

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

def deleteFile(fids):
    """
    params, data: {'fids': (list) list of file id}
    return, data: {}
    """
    for fid in fids:
        f = Files.objects(fileid=fid).first()
        if f:
            try:
                f.filedata.data.delete()
                f.delete()
            except OperationError:
                f.filedata.data.delete()
                f.delete()                