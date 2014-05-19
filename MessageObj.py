#!/usr/bin/python
#-*- coding: utf-8 -*-


class MessageObj(object):
    """docstring for MessageObj"""
    def __init__(self, sender, content, oid):
        super(MessageObj, self).__init__()
        self.sender = sender
        self.content = content
        self.mid = self.oid = oid
        self.delivered = False

    def deliver(self):
        self.delivered = True

    def updateMsgId(self, mid):
        self.mid = mid

    def compare(self, obj):
        if self.mid < obj.mid:
            return True
        else:
            if self.mid == obj.mid:
                return self.sender < obj.sender
            else:
                return False

    def generateKey(self):
        return str(self.oid) + self.sender

    def serializedString(self):
        return self.sender + '::' + self.content + '::' + str(self.mid)

if __name__ == '__main__':
    pass
