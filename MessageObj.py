#!/usr/bin/python
#-*- coding: utf-8 -*-


class MessageObj(object):
    """docstring for MessageObj"""
    def __init__(self, sender, content, oid, mid, bType):
        super(MessageObj, self).__init__()
        self.type = bType
        self.sender = sender
        self.content = content
        self.replier = None
        self.oid = oid
        self.mid = mid
        self.delivered = False

    def __init__(self, msg):
        super(MessageObj, self).__init__()
        msg_split = msg.split('::')

        #critical::format hard cord
        self.type = msg_split[0]
        self.sender = msg_split[1].split('_')[0]
        self.oid = msg_split[1].split('_')[1]
        self.mid = msg_split[2]
        if self.type == 'A':
            self.content = ''.join(msg_split[3:])
        else:
            self.content = ''
        if self.type == 'P':
            self.replier = msg_split[3]
        else:
            self.replier = None
        self.delivered = False

    def commit(self):
        self.delivered = True

    def updateMsgId(self, mid):
        self.mid = mid

    def uniqueId(self):
        return self.sender + str(self.oid)

    def smallerThan(self, obj):
        if obj is None:
            return self
        if self.mid < obj.mid:
            return True
        else:
            if self.mid == obj.mid:
                return self.generateKey() < obj.generateKey()
            else:
                return False

    def __str__(self):
        if self.type == 'A':
            return '::'.join((self.type, self.sender + '_' + str(self.oid), str(self.mid), self.content))
        elif self.type == 'F':
            return '::'.join((self.type, self.sender + '_' + str(self.oid), str(self.mid)))
        else:
            return '::'.join((self.type, self.sender + '_' + str(self.oid), str(self.mid), self.replier))

    #required interface for heap
    def generateKey(self):
        return self.uniqueId()

    def compare(self, obj):
        return self.smallerThan(obj)

    def setPriority(self, priority):
        self.updateMsgId(priority)
        self.commit()

if __name__ == '__main__':
    pass
