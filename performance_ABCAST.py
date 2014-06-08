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
from ABCASTManager import ABCASTManager
from LogManager import LogManager
import sys
import time

if __name__ != "__main__":
    exit()

# Test only
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

class Thread_recvGB(Thread):
    def __init__(self, cast_s):
        Thread.__init__(self)
        self.cast_s = cast_s
    def run(self):
        while True:
            print self.cast_s.recvGB()

class Thread_recvCB(Thread):
    def __init__(self, cast_s):
        Thread.__init__(self)
        self.cast_s = cast_s
    def run(self):
        while True:
            print self.cast_s.recvCB()


class read_pipe(Thread):
    def __init__(self, pipe):
        Thread.__init__(self)
        self.pipe = pipe
    def run(self):
        while True:
            print self.pipe.read()

class read_from_abcast(Thread):
    def __init__(self, pipe):
        Thread.__init__(self)
        self.ab = pipe
    def run(self):
        global threshold
        while True:
            print self.ab.read()
            threshold -= 1

#20 members at most
def main():

    global threshold
    threshold = 0

    user_id = sys.argv[1]
    index = int(user_id)

    #Port = 10000 + index
    ip_addr = "localhost"
    port = 10000 + index
    localaddr = (ip_addr, port)

    user_id = user_id.ljust(20)

    b = BroadCast()
    um = UserManager(b, localaddr, user_id)

        #Try to connect the other members
    for i in range(20):
        if i == index:
            continue #don't need to connect itself

        remote_uid = str(i).ljust(20)

        port = 10000 + i
        addr = (ip_addr, port)

        sock = um.add_user(addr, remote_uid)

#        if sock != None:
#            add_new_user_abcast_list(remote_uid)

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

    #Init ABCASTManager
    am = ABCASTManager(user_id, t_cast_s, um, LogManager())
    am.start()

    #Code from Tao
    #Daemon threading for keeping adding the users 
    am.addUser("321") #call for update
    print 'user_list', um.fetch_user_list()
    
    ua = user_add(um, am)
    ua.setDaemon(True)
    ua.start()
    #auto UserManager update user list

    #Init recvCB()
    #t_cb_recv = Thread_recvCB(t_cast_s)
    #t_cb_recv.setDaemon(True)
    #t_cb_recv.start()
    t_ab_reader = read_from_abcast(am)
    t_ab_reader.setDaemon(True)
    t_ab_reader.start()


    '''
    for k in range(1000):
        am.write(str(k))

    time.sleep(20)

    '''
    send = 0
    while True:
        if threshold > 20:
            continue
        am.write(str(send))
        send += 1
        threshold += 1
    

    #message 
    '''
    while True:
        message = raw_input()
        if (message == "userlist"):
            print "userManager", um.fetch_user_list()
            print "abcast", am.clientList
        if (message == ""):
            continue
        #t_cast_s.sendCB(message)
        am.write(message)
    '''
        
    #Init abcast

    while True:
        message = raw_input()
        if (message == "sync"):
            print [x.uniqueId() for x in am.processQueue.objects]
        try:
            exec(message)
        except:
            print 'error'

if __name__ == "__main__":
    main()





