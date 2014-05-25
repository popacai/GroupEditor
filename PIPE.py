#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import threading
class PIPE():
    def __init__(self):
        self.r, self.w = os.pipe()
        self.writer = os.fdopen(self.w, "w", 0)
        self.reader = os.fdopen(self.r, "r", 0)
        self.rlock = threading.Lock()
        self.wlock = threading.Lock()

    def read(self):
        #return os.read(self.r, 1024)
        self.rlock.acquire()
        data = self.reader.readline()[:-1]
        data = data.replace("\x01", "\n")
        self.rlock.release()
        return data
    def write(self, data):
        #os.write(self.w, data)
        #return
        self.wlock.acquire()

        data = data.replace("\n", "\x01")
        self.writer.write(data + "\n")
        self.wlock.release()
    def close(self):
        try:
            self.writer.close()
        except:
            pass

        try:
            self.reader.close()
        except:
            pass
    def __del__(self):
        self.close()


if __name__ == "__main__":
    p = PIPE()
    for i in range(10):
        p.write(str(i) * 100)
    for i in range(9):
        print p.read()+"*"
    p.close()
    print p.read()+"*"

