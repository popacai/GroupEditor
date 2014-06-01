#!/usr/bin/python
#-*- coding: utf-8 -*-
from PIPE import PIPE
from CASTSelecter import CASTSelecter
from Heap import Heap
import threading
from MessageObj import MessageObj
from MessageObj import fromStr
from UserManager import UserManager
import copy

import time
import random


class CustomThread (threading.Thread):
    def __init__(self, method, args=None):
        threading.Thread.__init__(self)
        self.method = method
        self.args = args

    def run(self):
        if self.args is None:
            self.method()
        else:
            self.method(self.args)


class ABCASTManager(object):
    """Manager for sending ABCAST"""
    def __init__(self, userId, castSelector, clientManager):
        super(ABCASTManager, self).__init__()
        self.clock = 0
        self.clockMutex = threading.Lock()

        self.userId = userId
        self.inputPipe = PIPE()
        self.outputPipe = PIPE()
        self.castManager = castSelector

        self.responseReceiver = {}
        self.receiverMutex = threading.Lock()

        self.clientList = clientManager.fetch_user_list()
        self.clientListMutex = threading.Lock()
        self.clientManager = clientManager

        self.processQueue = Heap()
        self.heapMutex = threading.Lock()

        self.recvProc = CustomThread(self._startReceiveMessage)
        self.sendProc = CustomThread(self._startSendBroadCast)

    def start(self):
        self.recvProc.setDaemon(True)
        self.sendProc.setDaemon(True)
        self.recvProc.start()
        self.sendProc.start()

    def read(self):
        #parsed value
        return self.outputPipe.read()

    def write(self, message):
        self.inputPipe.write(message)

    def quit(self):
        pass

    #for CT
    def block(self):
        pass

    def waitAllDone(self):
        pass

    def resume(self):
        pass

    def addUser(self, userId):
        self.clientListMutex.acquire()
        self.clientList = self.clientManager.fetch_user_list()
        self.clientListMutex.release()

    def removeUser(self, userId):
        pass

    def getGroupStatus(self):
        return ''

    def setGroupStatus(self, groupStatus):
        pass

    #block thread
    def _startReceiveMessage(self):
        while True:
            # print 'receiving msg'
            msg = self.castManager.recvCB()
            # print 'msg received'
            # print self.clientList
            msgObj = fromStr(msg)

            #selector
            #for A::
            if msgObj.type == 'A':
                # print '%s receive A-Msg %s' % (self.userId, msg)
                # self.clientListMutex.acquire()
                if msgObj.sender in self.clientList:
                    self.heapMutex.acquire()
                    self.processQueue.push(msgObj)
                    self.clockMutex.acquire()
                    clk = self.clock = max(self.clock, self.processQueue.maxObj.mid) + 1
                    self.clockMutex.release()
                    self.heapMutex.release()
                    obj = MessageObj(msgObj.sender, None, msgObj.oid, clk, 'P')
                    obj.replier = self.userId
                    self._sendMessageObjBroadCast(obj, msgObj.sender)
                    # print 'P msg sent'
                # self.clientListMutex.release()
            elif msgObj.type == 'P':
            #for P::
                # print '%s receive P-Msg %s' % (self.userId, msg)
                self.receiverMutex.acquire()
                if msgObj.uniqueId() in self.responseReceiver:
                    cList, lastObj = self.responseReceiver[msgObj.uniqueId()]
                    # print '%s wait for %s, %d left' % (self.userId, msgObj.uniqueId(), len(cList))
                    # print cList
                    if msgObj.replier in cList:
                        cList.remove(msgObj.replier)
                        if not lastObj or lastObj.smallerThan(msgObj):
                            self.responseReceiver[msgObj.uniqueId()] = (cList, msgObj)
                        if len(cList) == 0:
                            self._sendMessageObjBroadCast(MessageObj(self.userId, None, msgObj.oid, msgObj.mid, 'F'))
                            del self.responseReceiver[msgObj.uniqueId()]
                self.receiverMutex.release()
            #for F::
            else:
                # print '%s receive F-Msg %s' % (self.userId, msg)
                self.heapMutex.acquire()
                self.processQueue.update(msgObj.uniqueId(), msgObj.mid)
                # print '%s is ready: %s' % (self.processQueue.top().uniqueId(), self.processQueue.top().delivered)
                while (not self.processQueue.empty()) and self.processQueue.top().delivered:
                    committedObj = self.processQueue.pop()
                    # print committedObj.content
                    self.outputPipe.write(committedObj.content)
                self.heapMutex.release()

    #No lock allowed for this call if A::msg
    def _sendMessageObjBroadCast(self, msgObj, target=None):
        if msgObj.type == 'A':
            #are these locks neccessary?
            self.receiverMutex.acquire()
            self.clientListMutex.acquire()
            clist = copy.deepcopy(self.clientList)
            self.clientListMutex.release()
            self.responseReceiver[msgObj.uniqueId()] = (clist, None)
            self.receiverMutex.release()
        if target is None:
            # print 'msg sent'
            # print self.clientList
            self.castManager.sendCB(str(msgObj))
        else:
            self.castManager.sendCB(str(msgObj), target)

    #block thread
    def _startSendBroadCast(self):
        while True:
            msg = self.inputPipe.read()
            self.clockMutex.acquire()
            self.clock += 1
            msgObj = MessageObj(self.userId, msg, self.clock, self.clock, 'A')
            self.clockMutex.release()
            self._sendMessageObjBroadCast(msgObj)


class FakeCASTSelecter(object):
    def __init__(self, addr):
        # self.pipes = {}
        self.adapter = {'a': PIPE(), 'b': PIPE(), 'c': PIPE()}
        self.addr = addr

    def sendCB(self, data, addr=None):
        class Thread_sleep_random(threading.Thread):
            def __init__(self, method, pip):
                threading.Thread.__init__(self)
                self.method = method
                self.pip = pip

            def run(self):
                time.sleep(random.random())
                self.method(self.pip.read())

        if addr is None:
            self.adapter['a'].write(data)
            self.adapter['b'].write(data)
            self.adapter['c'].write(data)
            t1 = Thread_sleep_random(self.pipes['a'].write, self.adapter['a'])
            t2 = Thread_sleep_random(self.pipes['b'].write, self.adapter['b'])
            t3 = Thread_sleep_random(self.pipes['c'].write, self.adapter['c'])
            t1.start()
            t2.start()
            t3.start()
        else:
            p = self.pipes[addr]
            p.write(data)

    def recvCB(self):
        return self.pipes[self.addr].read()


class FakeClientList(object):
    """docstring for FakeClientList"""
    def __init__(self, addrList):
        self.clients = addrList

    def fetch_user_list(self):
        return copy.deepcopy(self.clients)


def writeA(args):
    for x in xrange(0, args[1]):
        args[0].write('A' + str(x))


def writeB(args):
    for x in xrange(0, args[1]):
        args[0].write('B' + str(x))


def writeC(args):
    for x in xrange(0, args[1]):
        args[0].write('C' + str(x))

if __name__ == '__main__':
    selectorA = FakeCASTSelecter('a')
    selectorB = FakeCASTSelecter('b')
    selectorC = FakeCASTSelecter('c')
    pa = PIPE()
    pb = PIPE()
    pc = PIPE()
    selectorA.pipes = {'a': pa, 'b': pb, 'c': pc}
    selectorB.pipes = {'a': pa, 'b': pb, 'c': pc}
    selectorC.pipes = {'a': pa, 'b': pb, 'c': pc}

    cm = FakeClientList(['a', 'b', 'c'])
    abcA = ABCASTManager('a', selectorA, cm)
    abcB = ABCASTManager('b', selectorB, cm)
    abcC = ABCASTManager('c', selectorC, cm)

    abcA.start()
    abcB.start()
    abcC.start()

    ta = CustomThread(writeA, [abcA, 500])
    tb = CustomThread(writeB, [abcB, 500])
    tc = CustomThread(writeC, [abcC, 500])

    ta.start()
    tb.start()
    tc.start()

    # print abcA.read()
    # print abcB.read()
    # print abcC.read()

    for x in xrange(0, 1500):
        am = abcA.read()
        bm = abcB.read()
        cm = abcC.read()
        if not (am == bm and bm == cm):
            print 'something went wrong'
        if x % 100 == 0:
            print '100 msg done'

    # for x in xrange(1,10):
    #     pass
    # print ''
    # for x in xrange(0, 11):
    #     print 'A_%d: %s' % (x, abcA.read())

    # print ''

    # for x in xrange(0, 11):
    #     print 'B_%d: %s' % (x, abcB.read())

    # print ''

    # for x in xrange(0, 11):
    #     print 'C_%d: %s' % (x, abcC.read())

    # print ''

    # selector = CASTSelecter(b, um)
    # manager = ABCASTManager()
    # manager.start()

    # manager.write('haha')
    # manager.write('wiz')
    # print manager.read()
    # print manager.read()
