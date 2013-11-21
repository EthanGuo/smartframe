#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db import Files
import uuid, hashlib
from mongoengine import OperationError
from mongoengine.context_managers import switch_db
from ..config import FILE_DB_NAME
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
    with switch_db(Files, FILE_DB_NAME) as File:
        fileid = generateUniqueID()
        new = File(fileid=fileid, filename=filename, content_type=content_type)
        new.filedata.new_file()
        new.filedata.write(filedata)
        new.filedata.close()
        try:
            new.save()
        except OperationError:
            new.save()
        return ('/file/' + fileid)

def fetchFileData(fileid):
    """
    params, data: {'fileid':(string)fileid}
    return, data: {'filedata':(bytes)filedata, 'filename': (string)filename, 'content_type': (string)type}
    """
    #If fileid is valid, return filedata, or return error
    with switch_db(Files, FILE_DB_NAME) as File:
        targetfile = File.objects(fileid=fileid).first()
        if targetfile:
            filedata = targetfile.filedata.read()
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
    with switch_db(Files, FILE_DB_NAME) as File:
        for fid in fids:
            f = File.objects(fileid=fid).first()
            if f:
                try:
                    f.filedata.delete()
                    f.delete()
                except OperationError:
                    f.filedata.delete()
                    f.delete()                