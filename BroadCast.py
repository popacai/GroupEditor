#!/usr/bin/python
#-*- coding: utf-8 -*-

#raw BoardCast class

from MTCP import MTCP
from PIPE import PIPE

class BroadCast():
    def __init__(self): 
        self.output_pipe = PIPE()
        self.signal_pipe = PIPE()

        self.mtcp = MTCP(self.output_pipe, self.signal_pipe)

        self.socks = {} #key=addr, value=socket
        self.input_pipes = {} #key=addr, value=input_pipes

    def add_addr(self, addr, sock):
        if addr in self.socks:
            print addr, "already in the socket list"
            return None# error

        self.socks[addr] = sock

        input_pipe = PIPE()
        self.input_pipes[addr] = input_pipe

        self.mtcp.new_connect(sock, addr, input_pipe)

    def remove_addr(self, addr):
        #This will send the socket.close()

        if addr not in self.socks:
            print addr, "not in the socket list"
            return False

        sock = self.socks[addr]
        input_pipe = self.input_pipes[addr]

        sock.close()
        input_pipe.close()

        self.mtcp.close(addr)
        del self.socks[addr]
        del self.input_pipes[addr]

        return True


    def get_addrs(self):
        return self.socks.keys()

    def get_sock(self, addr):
        if addr not in self.socks:
            return None
        return self.socks[addr]

    def get_pipe(self, addr):
        if addr not in self.input_pipes:
            return None
        return self.input_pipes[addr]

    def read(self):
        return self.output_pipe.read()

    def send(self, addr, message): #return the input_pipe
        if self.socks[addr] == None:
            self.output_pipe.write(message)
        if addr not in self.input_pipes:
            print addr, "not in input_pipe"
            return None

        input_pipe = self.input_pipes[addr]
        input_pipe.write(message)
        return input_pipe

    def sendall(self,message):
        return self.broadcast(message)
    def broadcast(self, message): #return how many message has been sent
        for addr in self.input_pipes:
            pipe = self.input_pipes[addr]
            try:
                pipe.write(message)
            except:
                self.remove_addr(addr)
        self.output_pipe.write(message)
        return len(self.input_pipes)

    def get_signal_message(self):
        return self.signal_pipe.read()

if __name__ == "__main__":
    import socket
    import sys
    from threading import Thread
    import time
    import random

    class Ticker(Thread):
        def __init__(self, b):
            Thread.__init__(self)
            self.b = b
        def run(self):
            count = 0
            while True:
                self.b.broadcast("GBCAST" + str(count))
                count += 1
                time.sleep(1)

    class func_thread(Thread):
        def __init__(self, func):
            Thread.__init__(self)
            self.func = func
        def run(self):
            while True:
                print self.func()

    class func_thread2(Thread):
        def __init__(self, func, argv1, argv2):
            Thread.__init__(self)
            self.func = func
            self.argv1 = argv1
            self.argv2 = argv2
        def run(self):
            print self.func(self.argv1, self.argv2)
 

    local_test_addr = ("localhost", 12222)

    if sys.argv[1] == "server":
        def delay_remove(bcast, addr):
            time.sleep(10)
            print 'remove addr', addr
            print bcast.remove_addr(addr)
            print bcast.get_addrs()


        bcast = BroadCast()

        f_t_signal = func_thread(bcast.get_signal_message)
        f_t_read = func_thread(bcast.read)
        f_t_signal.setDaemon(True)
        f_t_read.setDaemon(True)
        f_t_signal.start()
        f_t_read.start()


        ticker = Ticker(bcast)
        ticker.setDaemon(True)
        ticker.start()

        s = socket.socket()
        s.bind(local_test_addr)
        s.listen(10)

        test_flag = True
        while True:
            sock, addr = s.accept()
            bcast.add_addr(addr, sock)

            if test_flag == True:
                f_t_delay = func_thread2(delay_remove, bcast, addr)
                f_t_delay.setDaemon(True)
                f_t_delay.start()
                #test_flag = False
            print bcast.get_addrs()

    if sys.argv[1] == "client":
        bcast = BroadCast()
        s = socket.socket()
        s.connect(local_test_addr)
        bcast.add_addr(("1.2.3.4", 1234), s)
        while True:
            print bcast.read()

    if sys.argv[1] == "client2":
        s = socket.socket()
        s.connect(local_test_addr)
        for i in range(10):
            print s.recv(1500)

        s.close()
    if sys.argv[1] == "client3":
        s = socket.socket()
        s.connect(local_test_addr)
        bcast = BroadCast()
        fake_addr = ("1.2.3.4", 1234)
        bcast.add_addr(fake_addr, s)
        for i in range(10):
            bcast.send(fake_addr,str(i))
            time.sleep(1)
