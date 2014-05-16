#!/usr/bin/python
#-*- coding: utf-8 -*-

class PIPE():
    def __init__(self):
        pass

    def read(self):
        pass

    def write(self, data):
        pass

if __name__ == "__main__":
    p = PIPE()
    p.write("123")
    print `p.read()
