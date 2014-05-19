#!/usr/bin/python
#-*- coding: utf-8 -*-

#TRTCP and TSTCP

import socket
from threading import Thread
from PIPE import PIPE
import threading
import time

# Threading recv TCP
global END_TCP_FLAG
END_TCP_FLAG = "\n\r\n\r"
class TRTCP(Thread):
    def __init__(self, sock, addr, output_pipe, signal_pipe):
        Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        self.output_pipe = output_pipe
        self.signal_pipe = signal_pipe

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.signal_pipe.write("addr closed " + str(self.addr))
        except:
            pass


    def run(self):
        #self.sock.settimeout(5) # Don't wait too much time
        data = ""
        while True:
            try:
                data += self.sock.recv(1)
                if not data:
                    self.sock.close()
                    self.signal_pipe.write("socket_close:" + str(self.addr))
                    self.close()
                    # output_pipe message
                pos = data.find(END_TCP_FLAG)
                if (pos == -1):
                    continue
                data1 = data[:pos]
                data = data[pos+len(END_TCP_FLAG):]

            except socket.timeout, e:
                continue
            except:
                self.signal_pipe.write("socket_err:" + str(self.addr))
                self.sock.close()
                self.close()
                return

            try:
                self.output_pipe.write(data1)
            except:
                self.signal_pipe.write("output_pipe_err:" + str(self.addr))
                self.close()
                return

# Threading send TCP
class TSTCP(Thread):
    def __init__(self, sock, addr, input_pipe, signal_pipe):
        Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        self.input_pipe = input_pipe
        self.signal_pipe = signal_pipe
    
    def close(self):
        try:
            self.sock.close()
            self.input_pipe.close()
            self.signal_pipe.write("addr closed " + str(self.addr))
        except:
            pass
    def run(self): 
        while True:
            try:
                data = self.input_pipe.read()
            except:
                #self.input_pipe break;
                self.signal_pipe.write("input_pipe_err:" + str(self.addr))
                self.sock.close()
                break

            try:
                self.sock.sendall(data + END_TCP_FLAG)
            except:
                self.signal_pipe.write("socket_err:" + str(self.addr))
                self.sock.close()
                #self.sock break
                break


if __name__ == "__main__":
    '''
    testing:

    case 1: server, curl_test>
        output_pipe, and signal_pipe testing
    case 2: server, client
        ...
    case 3: chatting s-c
        as a toy
    '''


    import sys
    def pause_script():
        raw_input("pause")

    class read_pipe(Thread):
        def __init__(self, pipe):
            Thread.__init__(self)
            self.pipe = pipe
        def run(self):
            while True:
                print self.pipe.read()
        


    if sys.argv[1] == "server":
        signal_pipe = PIPE()
        output_pipe = PIPE()
        input_pipes = [PIPE(), PIPE(), PIPE()]
        #server
        server = socket.socket()
        server.bind(("localhost", 12222))
        server.listen(10)
        number = 0

        t_signal = read_pipe(signal_pipe)
        t_output = read_pipe(output_pipe)
        t_signal.setDaemon(True)
        t_output.setDaemon(True)
        t_signal.start()
        t_output.start()

        socket_list = []
        for i in range(3):
            client_sock, client_addr = server.accept()
            t1 = TSTCP(client_sock, client_addr, input_pipes[i], signal_pipe)
            t1.setDaemon(True)
            t1.start()

            t2 = TRTCP(client_sock, client_addr, output_pipe, signal_pipe)
            t2.setDaemon(True)
            t2.start()

        pause_script()

        for i in range(3):
            input_pipes[i].write(str(i))
        pause_script()

        #close the connection
        for i in socket_list:
            i.close()


    if sys.argv[1] == "curl_test":
        import os
        os.system("timeout 5 curl localhost:12222&")
        os.system("timeout 2 curl localhost:12222&")
        os.system("sleep 1; timeout 2 curl localhost:12222&")
        time.sleep(5)

    if sys.argv[1] == "client":
        addr = ("localhost", 12222)
        s = socket.socket()
        s.connect(addr)

        signal_pipe = PIPE()
        output_pipe = PIPE()
        input_pipe = PIPE()

        t_signal = read_pipe(signal_pipe)
        t_output = read_pipe(output_pipe)
        t_signal.setDaemon(True)
        t_output.setDaemon(True)
        t_signal.start()
        t_output.start()

        t1 = TSTCP(s, addr, input_pipe, signal_pipe)
        t1.setDaemon(True)
        t1.start()

        t2 = TRTCP(s, addr, output_pipe, signal_pipe)
        t2.setDaemon(True)
        t2.start()

        while True:
            message = raw_input("")
            if (message == "q"):
                break
            input_pipe.write(message)
        s.close()

    if sys.argv[1] == "server_c": #chatting server
        class forward_pipe(Thread):
            def __init__(self, src, dst):
                Thread.__init__(self)
                self.dst = dst
                self.src = src
            def run(self):
                while True:
                    data = self.src.read()
                    for each_dst in self.dst:
                        each_dst.write(data)

        signal_pipe = PIPE()
        output_pipe = PIPE()
        input_pipes = []
        #server
        server = socket.socket()
        server.bind(("localhost", 12222))
        server.listen(10)
        number = 0

        t_signal = read_pipe(signal_pipe)
        #t_output = read_pipe(output_pipe)
        t_output = forward_pipe(output_pipe, input_pipes)
        t_signal.setDaemon(True)
        t_output.setDaemon(True)
        t_signal.start()
        t_output.start()

        socket_list = []
        while True:
            client_sock, client_addr = server.accept()

            pipe = PIPE()
            input_pipes.append(pipe)
            t1 = TSTCP(client_sock, client_addr, pipe, signal_pipe)
            t1.setDaemon(True)
            t1.start()

            t2 = TRTCP(client_sock, client_addr, output_pipe, signal_pipe)
            t2.setDaemon(True)
            t2.start()



