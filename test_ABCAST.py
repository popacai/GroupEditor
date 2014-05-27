#!/usr/bin/python
#-*- coding: utf-8 -*-

'''
Test interface for ABCAST
    by taocai

python test_ABCAST.py [user_index(int)]

example:
    python test_ABCAST.py 1
    python test_ABCAST.py 2
    python test_ABCAST.py 3
    python test_ABCAST.py 4

    [uid is 10 characters]
    
    This will create a 4 members group

'''
from threading import Thread
from UserManager import UserManager
from BroadCast import BroadCast
from CASTSelecter import CASTSelecter
import sys
import time

if __name__ != "__main__":
    exit()

def add_new_user_abcast_list(user):
    print 'new user add', user
    pass
# Test used only 
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

            add_new_user_abcast_list(user)

class Thread_recvGB(Thread):
    def __init__(self, cast_s):
        Thread.__init__(self)
        self.cast_s = cast_s
    def run(self):
        while True:
            print self.cast_s.recvGB()
class read_pipe(Thread):
    def __init__(self, pipe):
        Thread.__init__(self)
        self.pipe = pipe
    def run(self):
        while True:
            print self.pipe.read()
     

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
    for i in range(20):
        if i == index:
            continue #don't need to connect itself

        remote_uid = str(i).ljust(10)

        port = 10000 + i
        addr = (ip_addr, port)

        sock = um.add_user(addr, remote_uid)

        if sock != None:
            add_new_user_abcast_list(remote_uid)

    user_list = um.temp_user_list
    um.update_user_list(user_list.keys(), um.view_id + 1)
    user_list, view_id = um.get_user_list()

    #Init CASTSelecter
    t_cast_s = CASTSelecter(b)
    t_cast_s.setDaemon(True)
    t_cast_s.start()

    #Init GBRecver
    t_gb_recv = Thread_recvGB(t_cast_s)
    t_gb_recv.setDaemon(True)
    t_gb_recv.start()

    print '====================================================='
    #message 
    while True:
        message = raw_input()
        t_cast_s.sendGB(message)

    #Init abcast

if __name__ == "__main__":
    main()





