#!/usr/bin/python
#-*- coding: utf-8 -*-
from PIPE import PIPE
from CASTSelecter import CASTSelecter
from Heap import Heap
import threading
from MessageObj import MessageObj
from UserManager import UserManager
import copy

import socket
from BroadCast import BroadCast


class CustomThread (threading.Thread):
    def __init__(self, method):
        threading.Thread.__init__(self)
        self.method = method

    def run(self):
        self.method()


class ABCASTManager(object):
    """Manager for sending ABCAST"""
    def __init__(self, userId, castSelector, clientManager):
        super(ABCASTManager, self).__init__()
        self.clock = 0
        self.userId = userId
        self.inputPipe = PIPE()
        self.outputPipe = PIPE()
        self.castManager = castSelector

        self.responseReceiver = {}
        self.receiverMutex = threading.Lock()

        self.clientList = []
        self.clientListMutex = threading.Lock()
        self.clientManager = clientManager

        self.processQueue = Heap()
        self.heapMutex = threading.Lock()

        self.recvProc = CustomThread(self._startReceiveMessage)
        self.sendProc = CustomThread(self._startSendBroadCast)

    def start():
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
            msg = self.castSelector.recvCB()
            msgObj = MessageObj(msg)

            #selector
            #for A::
            if msgObj.type == 'A':
                self.clientListMutex.acquire()
                if msgObj.uniqueId() in self.clientList:
                    self.heapMutex.acquire()
                    self.processQueue.push(msgObj)
                    self.heapMutex.release()
                    self._sendMessageObjBroadCast(MessageObj(msgObj.sender, None, msgObj.oid, self.clock, 'P'), msgObj.sender)
                self.clientListMutex.release()
            elif msgObj.type == 'P':
            #for P::
                self.receiverMutex.acquire()
                if msgObj.uniqueId() in self.responseReceiver:
                    cList, lastObj = self.responseReceiver[msgObj.uniqueId()]
                    if msgObj.replier in cList:
                        cList.remove(msgObj.replier)
                        if lastObj.smallerThan(msgObj):
                            self.responseReceiver[msgObj.uniqueId()] = (cList, msgObj)
                        if len(cList) == 0:
                            self._sendMessageObjBroadCast(MessageObj(self.userId, None, msgObj.oid, msgObj.mid, 'F'))
                            del self.responseReceiver[msgObj.uniqueId()]
                self.receiverMutex.release()
            #for F::
                self.heapMutex.acquire()
                self.processQueue.update(msgObj.uniqueId(), msgObj.mid)
                while self.processQueue.top().delivered:
                    committedObj = self.processQueue.pop()
                    self.outputPipe.write(committedObj.content)
                self.heapMutex.release()

    #No lock allowed for this call if A::msg
    def _sendMessageObjBroadCast(self, msgObj, target=None):
        if target is None:
            self.castManager.sendCB(str(msgObj))
        else:
            self.castManager.sendCB(str(msgObj), target)

        if msgObj.type == 'A':
            #are these locks neccessary?
            self.receiverMutex.acquire()
            self.clientListMutex.acquire()
            clist = copy.deepcopy(clientList)
            self.responseReceiver[msgObj.uniqueId()] = (clist, None)
            self.receiverMutex.release()
            self.clientListMutex.release()

    #block thread
    def _startSendBroadCast(self):
        while True:
            msg = self.inputPipe.read()
            self.clock = self.clock + 1
            msgObj = MessageObj(self.userId, msg, self.clock, self.clock, 'A')
            self._sendMessageObjBroadCast(msgObj)


if __name__ == '__main__':
    pass
    # ip_addr = "localhost"
    # port = 10000 + 5
    # localaddr = (ip_addr, port)

    # b = BroadCast()
    # um = UserManager(b, localaddr, user_id)

    # selector = CASTSelecter(b, um)
    # manager = ABCASTManager()
    # manager.start()

    # manager.write('haha')
    # manager.write('wiz')
    # print manager.read()
    # print manager.read()

