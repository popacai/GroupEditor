#!/usr/bin/python
#-*- coding:utf-8 -*-

from UserManager import UserManager
from CASTSelecter import CASTSelecter
from EBCASTManager import EBCASTManager
from AddrManager import AddrManager
from GBMessage import GBMessage
from ViewChange import ViewChange
import json
import threading
import time
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

recv_gbcast viewchange message
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

        #print 'UID', UID

        self.status = 0 #use status machine to control
        #self.status = 1
        self.ebcast = EBCASTManager(self.abcast, self, self.UID)

        self.viewchange = ViewChange(self.abcast, self)

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

        if (len(self.user_m.temp_user_list.keys()) == 1):
            self.status = 2


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
    def send_fetch_response(self, gb):
        request_user = gb.user_id
        message = GBMessage()
        message.view_id = self.user_m.view_id
        message.action = "fetch_response"
        #message.message = self.abcast.logManager.encodedRecord()
        message.message = self.abcast.fetchRecord()
        print 'fetch response', message.message

        str_message = message.__encode__()
        self.cast_s.sendGB(str_message, request_user)


    def send_fetch_all_data(self):
        message = GBMessage()
        message.view_id = self.user_m.view_id
        message.user_id = self.UID
        message.action = "fetch_request"
        message.message = "encode"

        str_message = message.__encode__()

        c = self.user_m.fetch_user_list()
        
        other_user = ""
        for user in c:
            if user is not self.UID:
                other_user = user

        self.cast_s.sendGB(str_message, other_user)

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
            print gb.user_id, gb.message
            pass
        if (gb.action == "kick"):
            #remote delete
            if (gb.view_id < self.user_m.view_id):
                print gb.view_id, self.user_m.view_id, ' view id is too old' 
                return
            if (gb.view_id > self.user_m.view_id):
                self.user_m.updateuser_dict(self.user_m.fetch_user_list(), gb.view_id)
            print 'kick', gb.message , "*"
            if (gb.user_id in self.user_m.fetch_user_list()):
                self.recv_delete_msg(gb.message, gb.user_id)

        if (gb.action == "ask for dict"):
            if (gb.user_id == self.UID):
                #self.send_user_dict()
                pass
            else:
                self.update_user_dict(gb.message)
                self.send_user_dict()

        if (gb.action == "dict"):
            if (gb.view_id > self.user_m.view_id):
                self.user_m.view_id = gb.view_id
            self.update_user_dict(gb.message)
            if self.status == 1:
                if (self.connect_user_dict()):
                    self.status = 2
                else:
                    print 'error!', 'cannot join the group, try again'
                    self.status = 0
            print 'status', self.status

        if (self.status == 2):
            print 'ready to send prepare'
            self.send_prepare()
            

        if (gb.action == "prepare"):
            print 'vid', gb.view_id
            print 'uid', gb.user_id
            print 'msg', gb.message
            if gb.view_id > self.user_m.view_id:
                self.viewchange.prepare(gb)
            else:
                print 'PREPARE', "old view id", gb.view_id
                pass

        if (gb.action == "prepare-ok"):
            print 'vid', gb.view_id
            print 'uid', gb.user_id
            print 'msg', gb.message
            if (self.viewchange.prepare_ok(gb)):
                #user_list = json.loads(gb.message)
                #self.user_m.uate_user_list(user_list)
                self.abcast.addUser("123")
                print 'abcast resume'
                self.abcast.resume()

        if (gb.action == "fetch_request"):
            print 'fetch data'
            #request the fetch
            #fetch local 
            #encode and send back
            self.send_fetch_response(gb)

        if (gb.action == "fetch_response"):
            if self.viewchange.joiner == True:
                if gb.view_id >= self.user_m.view_id:
                    #time.sleep(3)
                    print 'get fetched message'
                    self.viewchange.joiner = False
                    str_history = gb.message
                    t = self.abcast.logManager.decodedRecord(str_history)
                    self.abcast.synchronize(t)

                    gb.message = json.dumps(self.user_m.fetch_user_list())
                    print 'done'
                    #time.sleep(3)
                    self.abcast.start()
                    print 'send final prepare-ok'
                    self.send_prepare_ok(gb)
                else:
                    print 'old view'
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
    def send_prepare_ok(self, gb):
        message = gb

        message.view_id = self.user_m.view_id
        message.user_id = self.UID
        message.action = "prepare-ok"
        #message.message = str_user_list
        print 'ok', message.message

        str_message = message.__encode__()

        self.status = 11 
        self.cast_s.sendGB(str_message)

    def send_prepare(self):
        self.status = 10
        user_list = self.addrmanager.user_dict.keys()
        user_list.remove(self.UID)
        new_user_list = user_list + [self.UID]
        self.user_m.update_user_list(new_user_list, self.user_m.view_id + 1)

        message = GBMessage()

        message.view_id = self.user_m.view_id + 1
        
        message.user_id = self.UID
        message.action = "prepare"

        user_list = self.addrmanager.user_dict.keys()
        user_list.remove(self.UID)
        new_user_list = user_list + [self.UID]
        str_json = json.dumps(new_user_list)
        print "PREPARE", "new_user_list", new_user_list

        message.message = str_json

        str_message = message.__encode__()

        self.cast_s.sendGB(str_message)

    def send_kick_message(self, message):
        print 'ERR', 'SEND Kick Message', message
        kick_message = GBMessage()

        kick_message.view_id = self.user_m.view_id
        kick_message.user_id = self.UID
        kick_message.action = "kick"
        kick_message.message = "B" + message

        str_message = kick_message.__encode__()

        self.cast_s.sendGB(str_message)


    def recv_signal(self):
        user_to_kick = self.user_m.quit_user()

        #self detect
        print "ERR", "self detect", user_to_kick
        self.ebcast.foundError(user_to_kick)
        #TEMP
        #self.delete_user(user_to_kick)
    def recv_delete_msg(self, message, src):
        print 'ERR', "RECV delete message from", src, "msg:", message
        trim_message = message[1:]
        if message[0] == "B":
            message = self.ebcast.receiveErrorBroadCast(trim_message)
        if message[0] == "R":
            message = self.ebcast.receiveErrorReply(trim_message)

        if message == None:
            return
        else:
            kick_message = GBMessage()

            kick_message.view_id = self.user_m.view_id
            kick_message.user_id = self.UID
            kick_message.action = "kick"
            kick_message.message = "R" + message

            str_message = kick_message.__encode__()

            self.cast_s.sendGB(str_message, src)
           
        return
        '''
        self.lock_user_list.acquire()
        if user_to_kick in self.user_m.fetch_user_list():
            new_list = [user for user in self.user_m.fetch_user_list() if user != user_to_kick]
            #self.user_m.update_user_list(new_list, self.user_m.view_id)
            
            #del self.user_m.user_list[user_to_kick]
            #I don't check it.
            #Better to use update instead of this
            #self.user_m.b.remove_addr(user_to_kick)
        self.lock_user_list.release()
        '''

    def delete_user(self, user):
        print 'ERR', 'delete user', user
        userlist = self.user_m.fetch_user_list()
        try:
            userlist.remove(user)
        except:
            print user , 'is not in the userlist'
            pass

        self.user_m.update_user_list(userlist, self.user_m.view_id)
        self.addrmanager.remove_dict(user)
        #self.abcast.addUser("123")
        #print 'ERR', 'delete user done'
    
    def recheck_join_status(self):
        self.cond.acquire()
        self.cond.wait()
        self.cond.release()
        if self.viewchange.check_log():
            self.abcast.addUser("123")
            self.abcast.resume()
            #print 'abcast resume'


