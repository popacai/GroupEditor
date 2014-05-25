#!/usr/bin/python
#-*- coding: utf-8 -*-
from PIPE import PIPE
from BroadCast import BroadCast
from Heap import Heap
import threading
from MessageObj import MessageObj


class ABCASTManager(object):
    """Manager for sending ABCAST"""
    def __init__(self, addr):
        super(ABCASTManager, self).__init__()
        self.clock = 0
        self.inputPipe = PIPE()
        self.outputPipe = PIPE()
        self.clientList = {}
        self.clientLog = {}
        self.msgBroadCast = BroadCast()
        self.responseReceiver = {}
        self.processQueue = Heap()
        self.heapMutex = threading.Lock()

    def bindSockets(self, dic):
        self.clientList = dic
        for (k, v) in dic.items():
            self.msgBroadCast.add_addr(k, v)
        #todo::set log

    def read(self):
        #parsed value
        return self.outputPipe.read()

    def write(self, message):
        pass

    def quit(self):
        pass

    def run():
        pass

    #block thread
    def _startReceiveMessage(self, msg):
        while True:
            msg = self.msgBroadCast.read()
            msgObj = MessageObj(msg)

    #block thread
    def _startSendBroadCast(self, msg):
        while True:
            msg = self.inputPipe.read()
            msg.split()


    def isABCastResponse(msg):
        


if __name__ == '__main__':
    pass
