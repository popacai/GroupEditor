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
    
    def send_sync_response(self, client):
        #Send to all
        gb = GBMessage()
        gb.view_id = self.user_m.view_id
        gb.user_id = self.UID
        gb.action = "sync"
        
        print self.user_m.to_json()
        gb.message = self.user_m.to_json()

        str_message = str(gb)
        self.cast_s.sendGB(str_message, client)


    def send_sync_request(self):
        gb = GBMessage()
        gb.view_id = self.user_m.view_id
        gb.user_id = self.UID
        gb.action = "sync-req"
        gb.message = ""

        str_message = str(gb)
        self.cast_s.sendGB(str_message)

    def send_fetch_all_data(self):
        pass

    def notify_all(self):
        self.cond.acquire()
        self.cond.notify_all()
        self.cond.release()

    def recv_gbcast(self):
        #recv gbcast
        str_message = self.cast_s.recvGB()
        print 'message', str_message
        if len(str_message) < 1:
            return


        print "before message", self.user_m.get_user_list()

        gb = GBMessage().__decode__(str_message)
        #View ID is too old

        print "action", gb.action
        if (gb.action == "kick"):
            if (gb.view_id < self.user_m.view_id):
                print gb.view_id, self.user_m.view_id, ' view id is too old' 
                return
            print 'kick', gb.message , "*"
            if (gb.user_id in self.user_m.fetch_user_list()):
                self.delete_user(gb.message)

        if (gb.action == "sync"):
            self.lock_user_list.acquire()
            #TODO: lock please
            if (gb.view_id < self.user_m.view_id):
                print gb.view_id, self.user_m.view_id, ' view id is too old' 
                return
            
            new_l = self.user_m.to_list(gb.message)
            old_l = self.user_m.fetch_user_list()

            user_not_in_new = [user for user in old_l if user not in new_l]
            for user in user_not_in_new:
                self.send_kick_message(user)
                self.delete_user(user)

            self.user_m.update_user_list(new_l, gb.view_id)

            user_not_in_local = [user for user in new_l if user not in self.user_m.fetch_user_list()]

            for user in user_not_in_local:
                self.send_kick_message(user)
                self.delete_user(user)

            #kick the new nodes. 
            print 'after update', self.user_m.get_user_list()
            self.lock_user_list.release()

            #only kick the old nodes
            #update
            pass

        if (gb.action == "sync-req"):
            self.send_sync_response(gb.user_id)
            #send sync


        self.notify_all()
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
    def send_kick_message(self, user_to_kick):
        kick_message = GBMessage()

        kick_message.view_id = self.user_m.view_id
        kick_message.user_id = self.UID
        kick_message.action = "kick"
        kick_message.message = user_to_kick

        str_message = kick_message.__encode__()

        self.cast_s.sendGB(str_message)


    def recv_signal(self):
        user_to_kick = self.user_m.quit_user()

        self.send_kick_message(user_to_kick)
        self.delete_user(user_to_kick)
        '''
        read signal from the signal_pipe 
        call remove user
        '''
    def delete_user(self, user_to_kick):
        self.lock_user_list.acquire()
        if user_to_kick in self.user_m.fetch_user_list():
            new_list = [user for user in self.user_m.fetch_user_list() if user != user_to_kick]
            self.user_m.update_user_list(new_list, self.user_m.view_id)
            
            #del self.user_m.user_list[user_to_kick]
            #I don't check it.
            #Better to use update instead of this
            #self.user_m.b.remove_addr(user_to_kick)
        self.lock_user_list.release()

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
        


