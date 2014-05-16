#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
class PIPE():
    def __init__(self):
        self.r, self.w = os.pipe()
        self.writer = os.fdopen(self.w, "w", 0)
        self.reader = os.fdopen(self.r, "r", 0)

    def read(self):
        data = self.reader.readline()[:-1]
        data = data.replace("\x01", "\n")
        return data
    def write(self, data):
        data = data.replace("\n", "\x01")
        self.writer.write(data + "\n")


if __name__ == "__main__":
    p = PIPE()
    for i in range(10):
        p.write(str(i))
    while True:
        print p.read()+"*"
