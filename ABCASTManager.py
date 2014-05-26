#!/usr/bin/python
#-*- coding: utf-8 -*-
from PIPE import PIPE
from CASTSelector import CASTSelector
from Heap import Heap
import threading
from MessageObj import MessageObj


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
        self.inputPipe = PIPE()
        self.outputPipe = PIPE()
        self.responseReceiver = {}
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

    def block(self):
        pass

    def resume(self):
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


            #for P::
            if (sender + oid) in self.responseReceiver:
                msgObj, cnt = self.responseReceiver[sender + oid]
                #compare to replace
                if cnt == len(self.clientList) + 1:
                    #send F msg
                    del self.responseReceiver[sender + oid]
            else:

                if :
                    pass
                self.responseReceiver[sender + oid] = (msgObj, 

            #for F::


    #block thread
    def _startSendBroadCast(self):
        while True:
            msg = self.inputPipe.read()
            msg.split()


    def isABCastResponse(msg):
        return True


if __name__ == '__main__':
    pass
