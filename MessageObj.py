#!/usr/bin/python
#-*- coding: utf-8 -*-


class MessageObj(object):
    """docstring for MessageObj"""
    def __init__(self, sender, content, oid, mid, vid, bType):
        super(MessageObj, self).__init__()
        self.type = bType
        self.sender = sender
        self.content = content
        self.replier = None
        self.oid = oid
        self.mid = mid
        self.vid = vid
        self.delivered = False
        self.discard = False

    def commit(self):
        self.delivered = True

    def updateMsgId(self, mid):
        self.mid = mid

    def uniqueId(self):
        return self.sender + '_' + str(self.oid)

    def smallerThan(self, obj):
        if obj is None:
            return self
        if self.mid < obj.mid:
            return True
        else:
            if self.mid == obj.mid:
                return self.uniqueId() < obj.uniqueId()
            else:
                return False

    def __str__(self):
        if self.type == 'A':
            return '::'.join((self.type, self.sender + '_' + str(self.oid), str(self.mid), str(self.vid), self.content))
        elif self.type == 'F':
            return '::'.join((self.type, self.sender + '_' + str(self.oid), str(self.mid), str(self.vid)))
        else:
            return '::'.join((self.type, self.sender + '_' + str(self.oid), str(self.mid), str(self.vid), self.replier))

    #required interface for heap
    def generateKey(self):
        return self.uniqueId()

    def compare(self, obj):
        return self.smallerThan(obj)

    def setPriority(self, priority):
        self.updateMsgId(priority)
        self.commit()


def fromStr(msg):
    msg_split = msg.split('::')

    #critical::format hard cord
    newtype = msg_split[0]
    newsender = msg_split[1].split('_')[0]
    newoid = msg_split[1].split('_')[1]
    newmid = int(msg_split[2])
    newvid = int(msg_split[3])
    newreplier = None
    if newtype == 'A':
        newcontent = ''.join(msg_split[4:])
    else:
        newcontent = ''
    if newtype == 'P':
        newreplier = msg_split[4]
    else:
        newreplier = None
    newdelivered = False
    obj = MessageObj(newsender, newcontent, newoid, newmid, newvid, newtype)
    obj.replier = newreplier
    return obj

if __name__ == '__main__':
    pass
