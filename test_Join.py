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
            #self.um.view_id += 1
            #self.um.update_user_list(_temp, self.um.view_id)

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
    ip_addr, port = user_id.split(":")
    if len(ip_addr) == 0:
        ip_addr = '0.0.0.0'

    port = int(port)

    #Port = 10000 + index
    ip_addr = (ip_addr, port)
    localaddr = ip_addr
    user_id = str(ip_addr).ljust(20)
    user_id = user_id.replace(',', ':')


    remote_ip, remote_port = sys.argv[2].split(":")
    remote_port = int(remote_port)

    remote_ip_addr = (remote_ip, remote_port)
    remote_uid = str(remote_ip_addr).ljust(20)
    remote_uid = remote_uid.replace(',', ':')


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

        remote_uid = str(i).ljust(20)

        port = 10000 + i
        addr = (ip_addr, port)

        sock = um.add_user(addr, remote_uid)

        #if sock != None:
            #add_new_user_abcast_list(remote_uid)
    '''
    #offset = int(sys.argv[2])
    #remote_ip_addr = ("localhost", 10000 + offset)

    #remote_uid = str(offset).ljust(20)
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
    ab_m = ABCASTManager(user_id, t_cast_s, um, LogManager()) 
    ab_m.start()


    #ABCAST Reader
    t_ab_reader = read_from_abcast(ab_m)
    t_ab_reader.setDaemon(True)
    t_ab_reader.start()

    #Init GBCAST
    gb_m = GBCASTManager(user_id,t_cast_s, um, ab_m)

    t_gbcast = Thread_GBCAST(gb_m)
    t_gbcast.setDaemon(True)
    t_gbcast.start()

    print '====================================================='
    #message 
    count = 0
    while True:
        message = raw_input()
        if (message == "sync"):
            gb_m.send_user_dict_request()
        elif message == "clock":
            gb_m.test_clock(str(count))
            count += 1
        elif message == "userlist":
            #print gb_m.user_m.temp_user_list.keys()
            print gb_m.user_m.get_user_list()
        elif message == "prepare":
            gb_m.send_prepare()
        elif message == "prepare-ok":
            gb_m.send_prepare_ok()
        elif message == "abcast":
            print 'abcast'
            for i in xrange(10):
                ab_m.write(str(i))
        elif message == "command":
            while True:
                message = raw_input()
                if (message == "exit"):
                    break
                try:
                    exec(message)
                except:
                    print 'error'
        else:
            ab_m.write(message)


    #Init abcast

if __name__ == "__main__":
    main()





