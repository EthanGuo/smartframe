#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import threading
from Queue import Queue
import time

queue = Queue()
sessionlist = {'abcd-efgh': 12345678, }

def checkSessionList():
    print "checking session list"
    for session in sessionlist:
        if (time.time() - sessionlist[session]) > 600:
            print "Session has not been updated in 10mins, surppose its dead"

def updateSessionList(data):
    '''
        data: {'sid': (string)sid, 'uptime': (int)uptime}
    '''
    print "Updating session list"
    if data['sid'] in sessionlist:
        sessionlist[data['sid']] = data['uptime']
    else:
        sessionlist.update({data['sid']: data['uptime']}) 

def addHeartBeat(queue):
    server = redis.StrictRedis('127.0.0.1')
    client = server.pubsub()
    client.subscribe('session:heartbeat')
    for msg in client.listen():
        queue.put(msg['data'])

def addChecker(queue):
    while True:
        queue.put('check')
        time.sleep(10)
        
def worker(queue):
    while True:
        task = queue.get()
        if task == 'check':
            checkSessionList()
        else:
            updateSessionList(task)

def main():
    treceive = threading.Thread(target=addHeartBeat, args=(queue,))
    treceive.start()
    tcheck = threading.Thread(target=addChecker, args=(queue,))
    tcheck.start()
    tworker = threading.Thread(target=worker, args=(queue,))
    tworker.start()

if __name__ == '__main__':
    main()