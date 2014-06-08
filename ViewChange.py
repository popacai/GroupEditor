#!/usr/bin/python
#-*- coding:utf-8 -*-

from threading import Thread
import json
from GBMessage import GBMessage

class ViewChange(Thread):
    def __init__(self, abcast, gbcast):
        Thread.__init__(self)
        self.view_id = 0
        self.abcast = abcast
        self.gbcast = gbcast
        self.log = {}

    def prepare(self, gb):
        #Be called if recv a prepare
        #Sender and Recver
        if (gb.view_id >= self.view_id):


            self.gbcast.send_prepare_ok(gb)
            pass
        else:
            pass

    def prepare_ok(self, gb, new_user):
        all_done = False
        if (gb.view_id >= self.view_id):

            user_list = json.loads(gb.message)
            new_user = user_list[-1]
            if (insert_into_log(gb), new_user):
                all_done = True
        else:
            #old message
            pass

        return all_done
        #recv a prepare-ok message

    def insert_into_log(self, gb, new_user):
        view_id = str(gb.view_id) + new_user
        if gb.view_id not in self.log:
            self.log[view_id] = {}

        log = self.log[view_id]

        log[gb.user_id] = 1

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
           
    vc = ViewChange(FakeABCAST(), FakeGBCAST())
    gb = GBMessage()
    gb.view_id = 0
    gb.message = json.dumps(['a', 'b', 'c', 'd'])
    vc.prepare(gb)


