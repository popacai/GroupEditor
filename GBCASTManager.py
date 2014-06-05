#!/usr/bin/python
#-*- coding:utf-8 -*-

from UserManager import UserManager
from CASTSelecter import CASTSelecter
from AddrManager import AddrManager
from GBMessage import GBMessage
import json
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

        self.addrmanager = AddrManager(self.user_m.local_addr, UID)

        print 'UID', UID

        self.status = 0 #use status machine to control
        #self.status = 1
        pass

    def update_user_dict(self, message):
        user_dict = json.loads(message)
        self.addrmanager.update_dict(user_dict)

    def send_user_dict_request(self):
        self.status = 1
        user_dict = self.addrmanager.get_dict()
        str_json = json.dumps(user_dict)

        request_message = GBMessage()
        request_message.user_id = self.UID
        request_message.action = "ask for dict"
        request_message.message = str_json
        str_message = request_message.__encode__()
        self.cast_s.sendGB(str_message)

    def send_user_dict(self):
        user_dict = self.addrmanager.get_dict()
        #dumps to json format
        str_json = json.dumps(user_dict)

        dict_message = GBMessage()

        dict_message.view_id = self.user_m.view_id
        dict_message.user_id = self.UID
        dict_message.action = "dict"
        dict_message.message = str_json

        str_message = dict_message.__encode__()

        self.cast_s.sendGB(str_message)
    def connect_user_dict(self):
        user_dict = self.addrmanager.get_dict()
        for remote_uid in user_dict:
            if remote_uid not in self.user_m.temp_user_list \
                or remote_uid not in self.user_m.user_list:
                addr = (user_dict[remote_uid][0], user_dict[remote_uid][1])
                sock = self.user_m.add_user(addr, remote_uid)
                if sock == None:
                    return False

        return True 

    def test_clock(self, s):
        message = GBMessage()

        message.view_id = self.user_m.view_id
        message.user_id = self.UID
        message.action = "clock"
        message.message = s

        str_message = message.__encode__()

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
        if len(str_message) < 1:
            return

        gb = GBMessage().__decode__(str_message)
        #View ID is too old

        print "action", gb.action
        if (gb.action == "clock"):
            print gb.message
        if (gb.action == "kick"):
            #remote delete
            if (gb.view_id < self.user_m.view_id):
                print gb.view_id, self.user_m.view_id, ' view id is too old' 
                return
            print 'kick', gb.message , "*"
            if (gb.user_id in self.user_m.fetch_user_list()):
                self.delete_user(gb.message)

        if (gb.action == "ask for dict"):
            if (gb.user_id == self.UID):
                pass
            else:
                self.update_user_dict(gb.message)
                #pass
                self.send_user_dict()

        if (gb.action == "dict"):
            self.update_user_dict(gb.message)
            if self.status == 1:
                if (self.connect_user_dict()):
                    self.status = 2
                else:
                    print 'error!', 'cannot join the group, try again'
                    self.status = 0
        if (gb.action == "prepare"):
            #Read the message,
            #update the usermanager user_list
            #block abcast
            pass

        if (gb.action == "prepare-ok"):
            pass


        #check whether to prepare OK

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
    def send_kick_message(self, message):
        kick_message = GBMessage()

        kick_message.view_id = self.user_m.view_id
        kick_message.user_id = self.UID
        kick_message.action = "kick"
        kick_message.message = message

        str_message = kick_message.__encode__()

        self.cast_s.sendGB(str_message)


    def recv_signal(self):
        user_to_kick = self.user_m.quit_user()

        self.send_kick_message(user_to_kick)
        #self delete?
        self.delete_user(user_to_kick)
        '''
        read signal from the signal_pipe 
        call remove user
        '''
    def delete_user(self, user_to_kick):
        return
        self.lock_user_list.acquire()
        if user_to_kick in self.user_m.fetch_user_list():
            new_list = [user for user in self.user_m.fetch_user_list() if user != user_to_kick]
            #self.user_m.update_user_list(new_list, self.user_m.view_id)
            
            #del self.user_m.user_list[user_to_kick]
            #I don't check it.
            #Better to use update instead of this
            #self.user_m.b.remove_addr(user_to_kick)
        self.lock_user_list.release()


