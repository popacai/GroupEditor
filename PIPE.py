#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
class PIPE():
    def __init__(self):
        self.r, self.w = os.pipe()
        self.writer = os.fdopen(self.w, "w", 0)
        self.reader = os.fdopen(self.r, "r", 0)

    def read(self):
        #return os.read(self.r, 1024)
        data = self.reader.readline()[:-1]
        data = data.replace("\x01", "\n")
        return data
    def write(self, data):
        #os.write(self.w, data)
        #return
        data = data.replace("\n", "\x01")
        self.writer.write(data + "\n")
    def __del__(self):
        self.writer.close()
        self.reader.close()


if __name__ == "__main__":
    p = PIPE()
    for i in range(10):
        p.write(str(i) * 100)
    while True:
        print p.read()+"*"
