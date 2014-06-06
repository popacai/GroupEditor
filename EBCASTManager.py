#!/usr/bin/python
#-*- coding: utf-8 -*-
from LogManager import LogManager
from ErrorMessageObject import *
from ABCASTManager import ABCASTManager
import threading


class EBCASTManager(object):
    """docstring for EBCASTManager"""
    def __init__(self, abcManager, userId):
        super(EBCASTManager, self).__init__()
        self.abcManager = abcManager
        self.responseReceiver = {}
        self.receiverMutex = threading.Lock()
        self.userId = userId

    def sendErrorBroadCast(self, errMsg):
        pass

    def receiveErrorBroadCast(self, errMsg):
        errObj = fromString(errMsg)
        logManager = self.abcManager.logManager
        reply = errObj.sender + '::' + errObj.errorUser
        mList = []
        if errObj.errorUser in self.abcManager.clientList:
            self.abcManager.removeUser(errObj.errorUser)
            
            #todo::prepare error message and send
            #todo::build receiver
        for oid in errObj.msgList:
            status = logManager.msgStatus(errObj.errorUser, oid)
            if status is None:
                mList.add(str(-2))
            elif status == 'p':
                mList.add(str(-1))
            else:
                mList.add(status)
        if len(mList) > 0:
            reply = reply + '::' + '_'.join(mList)
        return reply

    def receiveErrorReply(self, errReply):
        errObj = fromString(errReply)
        self.receiverMutex.acquire()
        if errObj.errorUser in self.responseReceiver:
            cList = self.responseReceiver[errObj.errorUser][1]
            if errObj.sender in cList:
                currentList = self.responseReceiver[errObj.errorUser][0]
                cList.remove(errObj.sender)
                for i in xrange(0, len(errObj.msgList)):
                    if errObj.msgList[i] > 0:
                        currentList[i] = errObj.msgList[i]
                if len(cList) == 0:
                    if responseReceiver[errObj.errorUser][2]:
                        resendObj = ErrorMsgObject(self.userId, errObj.errorUser, [x[0] for x in responseReceiver[errObj.errorUser][0]])
                        del responseReceiver[errObj.errorUser]
                        self.sendErrorBroadCast(str(resendObj))
                    else:
                        self.abcManager.restoreData(errObj.errorUser, responseReceiver[errObj.errorUser][0])
                        del responseReceiver[errObj.errorUser]
        self.receiverMutex.release()

if __name__ == '__main__':
    pass
