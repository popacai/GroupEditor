#!/usr/bin/python
#-*- coding:utf-8 -*-

from threading import Thread
from UserManager import UserManager
from BroadCast import BroadCast
from CASTSelecter import CASTSelecter
from Monitor import Thread_GBCAST
from GBCASTManager import GBCASTManager
from ABCASTManager import ABCASTManager
import sys
import time

if __name__ != "__main__":
    exit()

# Test used only 
# auto update the user_list
class user_add(Thread):
    def __init__(self, um):
        Thread.__init__(self)
        self.um = um
        
    def run(self):
        while True:
            user = self.um.new_user()
            _temp = self.um.temp_user_list.keys()
            _temp.append(user)
            self.um.view_id += 1
            self.um.update_user_list(_temp, self.um.view_id)

            #add_new_user_abcast_list(user)


#20 members at most
def main():
    user_id = sys.argv[1]
    index = int(user_id)

    #Port = 10000 + index
    ip_addr = "localhost"
    port = 10000 + index
    localaddr = (ip_addr, port)

    user_id = user_id.ljust(10)

    b = BroadCast()
    um = UserManager(b, localaddr, user_id)

    #Daemon threading for keeping adding the users 
    ua = user_add(um)
    ua.setDaemon(True)
    ua.start()
    #auto UserManager update user list

    #Try to connect the other members
    #Testing version 1
    '''
    for i in range(20):
        if i == index:
            continue #don't need to connect itself

        remote_uid = str(i).ljust(10)

        port = 10000 + i
        addr = (ip_addr, port)

        sock = um.add_user(addr, remote_uid)

        #if sock != None:
            #add_new_user_abcast_list(remote_uid)
    '''
    offset = int(sys.argv[2])
    remote_ip_addr = ("localhost", 10000 + offset)

    remote_uid = str(offset).ljust(10)
    sock = um.add_user(remote_ip_addr, remote_uid)

    '''
    user_list = um.temp_user_list
    um.update_user_list(user_list.keys(), um.view_id + 1)
    user_list, view_id = um.get_user_list()
    '''

    #Init CASTSelecter
    t_cast_s = CASTSelecter(b)
    t_cast_s.setDaemon(True)
    t_cast_s.start()

    #Init ABCAST
    #fake
    #ab_m = ABCASTManager(user_id, t_cast_s, um) 
    ab_m = None

    #Init GBCAST
    gb_m = GBCASTManager(user_id,t_cast_s, um, ab_m)

    t_gbcast = Thread_GBCAST(gb_m)
    t_gbcast.setDaemon(True)
    t_gbcast.start()

    print '====================================================='
    #message 
    while True:
        message = raw_input()
        if (message == "sync"):
            gb_m.send_user_dict_request()
        else:
            t_cast_s.sendGB(message)

    #Init abcast

if __name__ == "__main__":
    main()





