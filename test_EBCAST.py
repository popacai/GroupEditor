#!/usr/bin/python
#-*- coding:utf-8 -*-

from threading import Thread
from UserManager import UserManager
from BroadCast import BroadCast
from CASTSelecter import CASTSelecter
from Monitor import Thread_GBCAST
from GBCASTManager import GBCASTManager
from ABCASTManager import ABCASTManager
from LogManager import LogManager
import sys
import time

if __name__ != "__main__":
    exit()
# Test used only 
class user_add(Thread):
    def __init__(self, um, am):
        Thread.__init__(self)
        self.um = um
        self.am = am
        
    def run(self):
        while True:
            user = self.um.new_user()
            _temp = self.um.temp_user_list.keys()
            _temp.append(user)
            self.um.view_id += 1
            self.um.update_user_list(_temp, self.um.view_id)

            self.am.addUser(user)
            print 'user_list:', self.um.fetch_user_list()
            #add_new_user_abcast_list(user)



class read_from_abcast(Thread):
    def __init__(self, pipe):
        Thread.__init__(self)
        self.ab = pipe
    def run(self):
        while True:
            print self.ab.read()



#20 members at most
def main():
    user_id = sys.argv[1]
    index = int(user_id)

    #Port = 10000 + index
    ip_addr = "localhost"
    port = 10000 + index
    localaddr = (ip_addr, port)

    user_id = user_id.ljust(20)

    b = BroadCast()
    um = UserManager(b, localaddr, user_id)

    #Daemon threading for keeping adding the users 
    #auto UserManager update user list

    #Try to connect the other members
    #Testing version 1
    for i in range(20):
        if i == index:
            continue #don't need to connect itself

        remote_uid = str(i).ljust(20)

        port = 10000 + i
        addr = (ip_addr, port)

        sock = um.add_user(addr, remote_uid)

        #if sock != None:
            #add_new_user_abcast_list(remote_uid)


    user_list = um.temp_user_list
    um.update_user_list(user_list.keys(), um.view_id + 1)
    user_list, view_id = um.get_user_list()

    #Init CASTSelecter
    t_cast_s = CASTSelecter(b)
    t_cast_s.setDaemon(True)
    t_cast_s.start()

    #Init ABCAST
    #fake
    ab_m = ABCASTManager(user_id, t_cast_s, um, LogManager()) 
    ab_m.start()

    ab_m.addUser("123")

    ua = user_add(um, ab_m)
    ua.setDaemon(True)
    ua.start()
    print 'user_list', um.fetch_user_list()
    #ab_m = None

    #Init GBCAST
    gb_m = GBCASTManager(user_id,t_cast_s, um, ab_m)

    t_gbcast = Thread_GBCAST(gb_m)
    t_gbcast.setDaemon(True)
    t_gbcast.start()

    print '====================================================='
    #ABCAST READER
    t_ab_reader = read_from_abcast(ab_m)
    t_ab_reader.setDaemon(True)
    t_ab_reader.start()
    #message 
    while True:
        message = raw_input()
        if message is "":
            continue
        if (message == "userlist"):
            print "userManager", um.fetch_user_list()
            print "abcast", ab_m.clientList
            continue
        if (message == "sync"):
            gb_m.send_user_dict_request()
            continue
        for i in range(1000):
            ab_m.write(message)
            

    #Init abcast

if __name__ == "__main__":
    main()





