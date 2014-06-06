#!/usr/bin/python
#-*- coding: utf-8 -*-


class ErrorMsgObject(object):
    """docstring for ErrorMsgObject"""
    def __init__(self, sender, errorUser, msgList):
        super(ErrorMsgObject, self).__init__()
        self.sender = sender
        self.errorUser = errorUser
        self.msgList = msgList

    def __str__(self):
        if len(self.msgList) == 0:
            return self.sender + '::' + self.errorUser
        else:
            return self.sender + '::' + self.errorUser + '::' + '_'.join([str(x) for x in self.msgList])


def fromString(errMsg):
    eleList = errMsg.split('::')
    sender = eleList[0]
    errorUser = eleList[1]
    if len(eleList) == 2:
        msgList = []
    else:
        midList = eleList[2].split('_')
        msgList = [int(m) for m in midList]
    return ErrorMsgObject(sender, errorUser, msgList)

if __name__ == '__main__':
    em = ErrorMsgObject('a', 'b', [1, 2, 3])
    print str(em)
    l = fromString(str(em)).msgList
    print l
