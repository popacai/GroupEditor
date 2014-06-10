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
        #self.rlock.acquire()
        data = self.reader.readline()[:-1]
        data = data.replace("\x01", "\n")
        #self.rlock.release()
        return data
    def write(self, data):
        #os.write(self.w, data)
        #return
        #self.wlock.acquire()

        data = data.replace("\n", "\x01")
        self.writer.write(data + "\n")
        #self.wlock.release()
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
    from threading import Thread
    count = 0
    global count
    class T(Thread):
        def __init__(self, pipe):
            Thread.__init__(self)
            self.pipe = pipe
        def run(self):
            global count
            while True:
                print self.pipe.read()
                count -= 1
    class W(Thread):
        def __init__(self, pipe):
            Thread.__init__(self)
            self.pipe = pipe
        def run(self):
            global count
            i = 0
            while True:
                self.pipe.write(str(i))
                count -= 1
                i += 1


    pipe = PIPE()
    t = T(pipe)
    t.setDaemon(True)
    t.start()

    t2 = T(pipe)
    t2.setDaemon(True)
    t2.start()

    w = W(pipe)
    w.setDaemon(True)
    w.start()

    i = 0
    while True:
        if (count > 20):
            continue
        pipe.write(str(i))
        count += 1
        i += 1


