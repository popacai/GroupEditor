#!/usr/bin/python
#-*- coding:utf-8 -*-

from threading import Thread

class ViewChange(Thread):
    def __init__(self, abcast, gbcast):
        Thread.__init__(self)
        self.view_id = 0
        self.abcast = abcast
        self.gbcast = gbcast
        Log = {}

    def prepare(self, view_id):
        pass

    def prepare_ok(self, view_id, user_id):
        pass

    def done(self):
        pass



