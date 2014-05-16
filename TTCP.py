#!/usr/bin/python
#-*- coding: utf-8 -*-

class TTCP():
    def __init__(self):
        pass
    
    def listen(self, addr):
        pass

    def connect(self, addr):
        print "connect", addr

    def send(self, data):
        print "send", data
        self.data = data
        
    def recv(self):
        return self.data

    def close(self):
        print "connect close"

    def __del__(self):
        pass



if __name__ == "__main__":
    ttcp = TTCP()
    ttcp.connect("12.1.1.1")
    ttcp.send("123")
    print ttcp.recv()
    ttcp.close()



