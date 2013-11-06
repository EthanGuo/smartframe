#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import threading
from Queue import Queue
import time, types, json
from smartserver.config import REDIS_HOST, REDIS_PORT
from smartserver.v1 import tasks

queue = Queue(25)
sessionlist = {}

def checkSessionList():
    print "Checking..."
    for sess in sessionlist.keys():
        if (time.time() - sessionlist[sess]) > 600:
            print "Session %s has not been updated in 10mins, surppose its dead" %sess
            tasks.ws_set_session_endtime.delay(sess)
            sessionlist.pop(sess)

def updateSessionList(msg):
    '''
        msg: {'sid': (string)sid}/{'clear': (string)sid}
    '''
    print "Updating session list now..."
    if 'sid' in msg.keys():
        sessionlist.update({msg['sid']: time.time()})
    elif 'clear' in msg.keys():
        sessionlist.pop(msg['clear']) 

def addHeartBeat(queue):
    con = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
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
        #After the connection's setup, a test signal would be sent, need to get rid of it.
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