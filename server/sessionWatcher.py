#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import threading
from Queue import Queue
import time, types, json
from smartserver.config import REDIS_URI

queue = Queue()
sessionlist = {}

def checkSessionList():
    print "Checking session list now..."
    for session in sessionlist.keys():
        if (time.time() - sessionlist[session]) > 600:
            print "Session %s has not been updated in 10mins, surppose its dead" %session
            sessionlist.pop(session)

def updateSessionList(msg):
    '''
        msg: {'sid': (string)sid}
    '''
    print "Updating session list now..."
    sessionlist.update({msg['sid']: time.time()}) 

def addHeartBeat(queue):
    #con = redis.StrictRedis(REDIS_URI.strip().replace(""))
    con = redis.StrictRedis('127.0.0.1')
    pubs = con.pubsub()
    pubs.subscribe('session:heartbeat')
    for msg in pubs.listen():
        queue.put(msg['data'])

def addChecker(queue):
    while True:
        queue.put('check')
        time.sleep(30)
        
def worker(queue):
    while True:
        msg = queue.get()
        if msg == 'check':
            checkSessionList()
        elif type(msg) is types.StringType:
            updateSessionList(json.loads(msg))

def main():
    treceive = threading.Thread(target=addHeartBeat, args=(queue,))
    treceive.start()
    tcheck = threading.Thread(target=addChecker, args=(queue,))
    tcheck.start()
    tworker = threading.Thread(target=worker, args=(queue,))
    tworker.start()

if __name__ == '__main__':
    main()