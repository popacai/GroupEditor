#!/usr/bin/python
#-*- coding:utf-8 -*-

from UserManager import UserManager
from CASTSelecter import CASTSelecter
from GBMessage import GBMessage
import threading
'''
detect user add
    #This is the leader <- the new client join in the group
    
    send_all(view change[prepare]) #including itself

    view change[done] messages from N nodes

    send_all(view change)
    view change
    block local
    resume if collect all ack
    
detect user remove
    send_all(kick user)

recv_gbcast view_change message
    view change message
    ...

recv gbcast kick message
    kick user
    
function for user add

'''
class GBCASTManager():
    def __init__(self, UID, cast_s, user_m, abcast):
        self.UID = UID
        self.cast_s = cast_s 
        self.user_m = user_m
        self.abcast = abcast

        #Rlock is used in here
        #condition will be notify once a GBCast message arrives
        self.lock_user_list = threading.Lock()
        self.cond = threading.Condition(self.lock_user_list)

        print 'UID', UID
        pass
    
    def send_sync_request(self):
        pass

    def send_sync_user_list(self):
        #return sync list
        pass

    def send_fetch_all_data(self):
        pass

    def recv_gbcast(self):
        #recv gbcast
        str_message = self.cast_s.recvGB()
        print 'message', str_message

        self.cond.acquire()
        self.cond.notify_all()
        self.cond.release()

        print "before message", self.user_m.get_user_list()

        gb = GBMessage().__decode__(str_message)
        #View ID is too old
        if (gb.view_id < self.user_m.view_id):
            print gb.view_id, self.user_m.view_id, ' view id is too old' 
            return

        if (gb.action == "kick"):
            print 'kick', gb.message , "*"
            if (gb.user_id in self.user_m.fetch_user_list()):
                self.delete_user(gb.message)

        if (gb.action == "sync"):
            pass

        '''
        send condition event
        sync-request
            send sync_user_list to all
        prepare
            call new user add
        done #prepare-ok
            log history done
            call new user add
        kick
            call remove user
        fetch
            if (view_id) is equal
                send all the data to that server
        '''
        pass

    def recv_signal(self):
        user_to_kick = self.user_m.quit_user()
        kick_message = GBMessage()

        kick_message.view_id = self.user_m.view_id
        kick_message.user_id = self.UID
        kick_message.action = "kick"
        kick_message.message = user_to_kick

        str_message = kick_message.__encode__()

        self.cast_s.sendGB(str_message)
        self.delete_user(user_to_kick)
        '''
        read signal from the signal_pipe 
        call remove user
        '''
    def delete_user(self, user_to_kick):
        #self.lock_user_list.acquire()
        if user_to_kick in self.user_m.fetch_user_list():
            new_list = [user for user in self.user_m.fetch_user_list() if user != user_to_kick]
            self.user_m.update_user_list(new_list, self.user_m.view_id)
            
            #del self.user_m.user_list[user_to_kick]
            #I don't check it.
            #Better to use update instead of this
            #self.user_m.b.remove_addr(user_to_kick)
        #self.lock_user_list.release()

    def update_user_list(self):
        '''
        if view_id is new
            old_thread.quit()
            update user_manager_user_list
            block abcast
            do
                wait until recv all prepare-ok(done) message
            while (if condition listen)
            update abcast
            resume abcast
        '''
        pass
        


