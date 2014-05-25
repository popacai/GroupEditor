#!/usr/bin/python
#-*- coding: utf-8 -*-

from threading import Thread
from BroadCast import BroadCast
from PIPE import PIPE

class CASTSelecter(Thread):
    def __init__(self, broadcast):
        Thread.__init__(self)
        self.cbpipe = PIPE()
        self.gbpipe = PIPE()
        self.abpipe = PIPE()
        self.b = broadcast
    def sendCB(self, data, addr = None):
        _data = "CBCAST" + data
        if addr == None:
            self.b.sendall(_data)
        else:
            self.b.send(addr, _data)
    def sendGB(self, data, addr = None):
        _data = "GBCAST" + data
        if addr == None:
            self.b.sendall(_data)
        else:
            self.b.send(addr, _data)

    def sendAB(self, data, addr = None):
        pass


    def recvCB(self):
        return self.cbpipe.read()
    def recvGB(self):
        return self.gbpipe.read()

    def recv(self):
        _data = self.b.read()
        header = _data[:6]
        data = _data[6:]
        if header == "CBCAST":
            self.cbpipe.write(data)
        if header == "GBCAST":
            self.gbpipe.write(data)

    def run(self):
        while True:
            self.recv()
        

if __name__ == "__main__":
    import socket
    import time
    import sys
    if sys.argv[1] == "client1":
        b = BroadCast()

        for i in range(10):
            sock = socket.socket()
            sock.connect(("localhost", 12222))
            b.add_addr(str(i), sock)

        cast = CASTSelecter(b)
        cast.setDaemon(True)
        cast.start()

        cast.sendGB("123")
        time.sleep(5)
    if sys.argv[1] == "client2":
        b = BroadCast()
        for i in range(1):
            sock = socket.socket()
            sock.connect(("localhost", 12222))
            b.add_addr(str(i), sock)
        cast = CASTSelecter(b)
        cast.setDaemon(True)
        cast.start()
        while True:
            print cast.recvGB()


