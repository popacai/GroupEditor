#!/usr/bin/python
#-*- coding: utf-8 -*-

from threading import Thread
from GBCASTManager import GBCASTManager
import thread
class Thread_GBCAST(Thread):
    def __init__(self, gbcast_m):
        Thread.__init__(self)
        self.gbcast_m = gbcast_m

    def close(self):
        thread.exit()
    def run(self):
        t_gb_recver = GB_Recever(self.gbcast_m)
        t_gb_recver.setDaemon(True)
        t_gb_recver.start()

        t_gb_signal = GB_Signal(self.gbcast_m)
        t_gb_signal.setDaemon(True)
        t_gb_signal.start()
        #creat signal thread
        #creat recver thread
        t_gb_recver.join()
        t_gb_signal.join()

class GB_Recever(Thread):
    def __init__(self, gbcast_m):
        Thread.__init__(self)
        self.gbcast_m = gbcast_m
    def run(self):
        while True:
            self.gbcast_m.recv_gbcast()

class GB_Signal(Thread):
    def __init__(self, gbcast_m):
        Thread.__init__(self)
        self.gbcast_m = gbcast_m
    def run(self):
        while True:
            print 'Monitor', 'RECV SIGNAL'
            self.gbcast_m.recv_signal()
