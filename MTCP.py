#!/usr/bin/python
#-*- coding: utf-8 -*-

from threading import Thread

class MTCP():
    def __init__(self, output_pipe, signal_pipe):
        #All the message we have received, we will write to output_pipe
        self.output_pipe = output_pipe
        self.signal_pipe = signal_pipe

        self.tr_list = []
        self.ts_list = []

    def new_connect(self, sock, addr, input_pipe):
        #This will create connection with addr
        #It will auto fetch data from input_pipe
        
        tr = TRTCP(sock, addr, self.output_pipe, self.signal_pipe)
        ts = TSTCP(sock, addr, input_pipe, self.signal_pipe)

        tr.setDaemon(True)
        ts.setDaemon(True)

        tr.start()
        ts.start()

        self.tr_list.append(tr)
        self.ts_list.append(ts)


if __name__ == "__main__":
    pass


