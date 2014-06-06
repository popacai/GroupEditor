#!/usr/bin/python
#-*- coding: utf-8 -*-
# from MessageObj import MessageObj


class Heap(object):
    """Custom heap for Msg object, support update"""
    def __init__(self):
        super(Heap, self).__init__()
        self.objects = []
        self.maxObj = None
        self.dic = {}

    def push(self, obj):
        if not self.maxObj is None:
            obj.mid = self.maxObj.mid + 1
        self.maxObj = obj
        key = obj.generateKey()
        if key in self.dic:
            return
        self.dic[key] = obj
        self.objects.append(obj)

    def pop(self):
        if self.empty():
            return None
        obj = self.objects[0]
#        print 'pop ' + obj.serializedString()
        key = obj.generateKey()
        del self.dic[key]
        self.objects[0] = self.objects[-1]
        del self.objects[-1]

 #       print self.objects[0].serializedString()

        if self.empty():
            self.maxObj = None
        else:
            self._parseDown(0)
        return obj

    def empty(self):
        return len(self.objects) == 0

    def top(self):
        if self.empty():
            return None
        return self.objects[0]

    def update(self, key, priority):
        if not key in self.dic:
            return
        obj = self.dic[key]
        idx = self.objects.index(obj)
        obj.setPriority(priority)
        # obj.mid = priority
        self._parseDown(idx)
        if self.maxObj.compare(obj):
            self.maxObj = obj
        # if obj.mid > self.maxObj.mid:
        #     self.maxObj = obj

    def getAllObjects(self):
        return self.objects

    def _parseDown(self, idx):
        size = len(self.objects)
        if size == 0 or idx >= size:
            return
        obj = self.objects[idx]
        while idx * 2 + 2 < size:
            lc = self.objects[idx * 2 + 1]
            rc = self.objects[idx * 2 + 2]
            if lc.compare(rc):
                if lc.compare(obj):
                    self.objects[idx] = lc
                    idx = idx * 2 + 1
                else:
                    self.objects[idx] = obj
                    break
            else:
                if rc.compare(obj):
                    self.objects[idx] = rc
                    idx = idx * 2 + 2
                else:
                    self.objects[idx] = obj
                    break
        if idx * 2 + 1 == size - 1:
            c = self.objects[size - 1]
            if c.compare(obj):
                self.objects[idx] = c
                self.objects[idx * 2 + 1] = obj
            else:
                self.objects[idx] = obj
        else:
            self.objects[idx] = obj

if __name__ == '__main__':
    pass
    # h = Heap()
    # obj1 = MessageObj('a', 'hello', 1)
    # obj2 = MessageObj('b', 'hi', 2)
    # obj3 = MessageObj('a', 'haha', 3)
    # obj4 = MessageObj('c', 'hello', 4)
    # obj5 = MessageObj('b', 'yes', 5)
    # obj6 = MessageObj('d', 'hello', 6)
    # h.push(obj1)
    # h.push(obj2)
    # h.push(obj3)
    # h.push(obj4)
    # h.push(obj5)
    # h.push(obj6)
    # h.update(obj3.generateKey(), 7)
    # h.update(obj1.generateKey(), 6)
    # while not h.empty():
    #     obj = h.pop()
    #     print obj.serializedString()
