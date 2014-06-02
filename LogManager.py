#!/usr/bin/python
#-*- coding: utf-8 -*-
import threading


class LogManager(object):
    """docstring for LogManager"""
    def __init__(self):
        super(LogManager, self).__init__()
        self.mutex = threading.Lock()
        self.prepared = {}
        self.delivered = {}

    def insertPrepare(self, sender, oid):
        self.mutex.acquire()
        if sender in self.prepared:
            msgList = self.prepared[sender]
            if not oid in msgList:
                msgList.append(oid)
        else:
            self.prepared[sender] = [oid]
        self.mutex.release()

    def insertDelivery(self, sender, oid):
        self.mutex.acquire()
        if sender in self.delivered:
            msgList = self.delivered[sender]
            if not oid in msgList:
                msgList.append(oid)
        else:
            self.delivered[sender] = [oid]
        self.mutex.release()

    def removePrepare(self, sender, oid):
        self.mutex.acquire()
        if sender in self.prepared:
            msgList = self.prepared[sender]
            if oid in msgList:
                msgList.remove(oid)
            if len(msgList):
                del self.prepared[sender]
        self.mutex.release()

    def updatePrepare(self, sender, oid):
        self.removePrepare(sender, oid)
        self.insertDelivery(sender, oid)

    #0 for none, 1 for prepare, 2 for delivered
    def msgStatus(self, sender, oid):
        if sender in self.prepared:
            msgList = self.prepared[sender]
            if oid in msgList:
                return 1
        if sender in self.delivered:
            msgList = self.delivered[sender]
            if oid in msgList:
                return 2
        return 0

if __name__ == '__main__':
    m = LogManager()
    m.prepared = {'a':[0, 1], 'b':[1]}
    m.delivered = {'b':[0], 'c': [0, 1]}

    m.insertPrepare('b', 2)
    print 'b_2: ', m.msgStatus('b', 2)
    m.insertPrepare('c', 2)
    print 'c_2: ', m.msgStatus('c', 2)
    print 'c_1: ', m.msgStatus('c', 1)
    print 'a_0: ', m.msgStatus('a', 0)
    m.updatePrepare('a', 0)
    print 'a_0: ', m.msgStatus('a', 0)
    print 'a_1: ', m.msgStatus('a', 1)
    m.removePrepare('a', 1)
    print 'a_1: ', m.msgStatus('a', 1)
    print 'c_3: ', m.msgStatus('c', 3)




