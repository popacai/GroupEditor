#!/usr/bin/python
#-*- coding: utf-8 -*-


from threading import Thread
class Monitor_user_add(Thread):
    def __init__(self, user_m):
        Thread.__init__(self)
        self.user_m = user_m

    def run(self):
        pass

class Monitor_user_quit(Thread):
    def __init__(self, user_m):
        Thread.__init__(self)
        self.user_m = user_m
    def run(self):
        pass
