#!/usr/bin/python
#-*- coding:utf-8 -*-

from threading import Thread
import json
from GBMessage import GBMessage
from UserManager import UserManager
import time

class wait_to_send_prepare_ok(Thread):
    def __init__(self, abcast, gbcast, gb):
        Thread.__init__(self)
        self.abcast = abcast
        self.gbcast = gbcast
        self.gb = gb # delay to send the gb message
    def run(self):
        #self.abcast.wait_done()
        #self.abcast.update_user_list()
        time.sleep(1)
        self.gbcast.send_prepare_ok(self.gb)

class ViewChange():
    def __init__(self, abcast, gbcast):
        #Thread.__init__(self)
        self.view_id = 0
        self.abcast = abcast
        self.gbcast = gbcast
        self.log = {}

    def prepare(self, gb):
        #Be called if recv a prepare
        #Sender and Recver
        if (gb.view_id > self.view_id):
            user_list = json.loads(gb.message)
            user_list = user_list + self.gbcast.user_m.fetch_user_list()
            self.gbcast.user_m.update_user_list(user_list, gb.view_id)
            print 'abcast block'
            #self.abcast.block()
            w = wait_to_send_prepare_ok(self.abcast, self.gbcast, gb)
            w.setDaemon(True)
            w.start()
        else:
            print 'old view'

    def prepare_ok(self, gb):
        new_user = ""
        all_done = False
        if (gb.view_id >= self.view_id):
            user_list = json.loads(gb.message)
            new_user = user_list[-1]
            if (self.insert_into_log(gb, new_user)):
                all_done = True
        else:
            #old message
            pass

        return all_done
        #recv a prepare-ok message

    def insert_into_log(self, gb, new_user):
        #view_id = str(gb.view_id) + new_user
        view_id = str(gb.view_id).ljust(10) + new_user
        if gb.view_id not in self.log:
            self.log[gb.view_id] = {}

        self.log[gb.view_id][gb.user_id] = 1
        log = self.log[gb.view_id]

        #check status?
        user_list = self.gbcast.user_m.fetch_user_list()
        for user in user_list:
            if user not in log:
                return False
        return True
    def done(self):
        pass


if __name__ == "__main__":
    class FakeUserManager():
        def __init__(self):
            pass
        def fetch_user_list():
            return ['a', 'b', 'c']

    class FakeGBCAST():
        def __init__(self):
            self.user_m = FakeUserManager()
        def send_prepare_ok(self, message):
            print 'send prepare ok', message
    class FakeABCAST():
        def block():
            print 'block local'
           
    #Prepare OK
    vc = ViewChange(FakeABCAST(), FakeGBCAST())
    gb = GBMessage()
    gb.view_id = 1
    gb.user_id = 'a'
    gb.message = json.dumps(['a', 'b', 'c', 'd'])
    vc.prepare(gb)


    #


