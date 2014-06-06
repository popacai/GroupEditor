#!/usr/bin/python
#-*- coding: utf-8 -*-
from LogManager import LogManager
from ErrorMessageObject import *
from ABCASTManager import ABCASTManager
import threading
import copy


class EBCASTManager(object):
    """docstring for EBCASTManager"""
    def __init__(self, abcManager, gbcManager, userId):
        super(EBCASTManager, self).__init__()
        self.abcManager = abcManager
        self.gbcManager = gbcManager
        self.responseReceiver = {}
        self.receiverMutex = threading.Lock()
        self.userId = userId

    #To delete gbcManager's userlist
    #self.gbcManager.delete_user(username)
    def sendErrorBroadCast(self, errMsg):
        self.gbcManager.send_kick_message(errMsg)

    def foundError(self, errUser):
        if errUser in self.abcManager.clientList:
            self.gbcManager.delete_user(errUser)
            self.abcManager.removeUser(errUser)
            bcMsg = self.userId + '::' + errUser
            oidList = self.abcManager.logManager.prepared[errUser]
            if not oidList is None:
                msgContent = '_'.join([str(x) for x in oidList])
                bcMsg = bcMsg + msgContent
                cList = copy.deepcopy(self.abcManager.clientList)
                self.receiverMutex.acquire()
                responseReceiver[errUser] = ([(oid, -1) for oid in oidList], cList, False)
                self.receiverMutex.release()
                self.sendErrorBroadCast(bcMsg)

    def receiveErrorBroadCast(self, errMsg):
        errObj = fromString(errMsg)
        logManager = self.abcManager.logManager
        reply = errObj.sender + '::' + errObj.errorUser
        mList = []
        if errObj.errorUser in self.abcManager.clientList:
            self.gbcManager.delete_user(errObj.errorUser)
            self.abcManager.removeUser(errObj.errorUser)
            bcMsg = self.userId + '::' + errObj.errorUser
            oidList = logManager.prepare[errObj.errorUser]
            if not oidList is None:
                msgContent = '_'.join([str(x) for x in oidList])
                bcMsg = bcMsg + msgContent
                self.receiverMutex.acquire()
                responseReceiver[errUser] = ([(oid, -1) for oid in oidList], cList, False)
                self.receiverMutex.release()
                self.sendErrorBroadCast(bcMsg)
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
                        self.abcManager.logManager.removeUser(errObj.errorUser)
                        del responseReceiver[errObj.errorUser]
        self.receiverMutex.release()

if __name__ == '__main__':
    pass
