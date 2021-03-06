#!/usr/bin/python
#-*- coding: utf-8 -*-

from threading import Thread
from BroadCast import BroadCast
from PIPE import PIPE
import socket
import time
import json
import threading
    
class UserManager():
    def __init__(self, broadcast ,addr, UID):
        self.b = broadcast

        self.UID = UID.ljust(20)

        self.local_addr = addr

        self.lock = threading.Lock()

        self.temp_user_list = {}
        self.user_list = {}
        self.kicked_user_list = []

        self.t_ll = LocalListener(self.local_addr, self.temp_user_list)
        self.t_ll.setDaemon(True)
        self.t_ll.start()

        self.view_id = 0

        time.sleep(1)

        sock = self.t_ll.connect(self.local_addr, self.UID)
        u = self.t_ll.new_user()
        self.b.add_addr(u, None) #send loopback
        #self.b.add_addr(u, sock)
        
        self.new_group = False
        if u == self.UID:
            #print 'succeed to connect itself'
            pass
        else:
            #print 'error to add self'
            pass

    def add_user(self, addr, remote_uid):
        s = cast_connect(addr, self.UID)
        if s == None:
            #print "unable to connect", addr
            return None
        
        self.temp_user_list[remote_uid] = s
        self.b.add_addr(remote_uid, s)
        #print "temp" , self.temp_user_list
        return s

    def new_user(self):
        uid = self.t_ll.new_user()
        self.b.add_addr(uid, self.temp_user_list[uid])
        return uid

    def quit_user(self):
        while True:
            data = self.b.get_signal_message()
            items = data.split(',')
            if len(items) != 2:
                #print "error!", data
                pass
            
            UID = items[1]

            if UID in self.user_list:
                return UID

    #Yan
    def fetch_user_list(self):
        return self.user_list.keys()

    def get_user_list(self):
        return self.user_list.keys()[:], self.view_id

    def to_json(self, l = None):
        if l == None:
            l = self.user_list.keys()
        return json.dumps(l)

    def to_list(self, message):
        l = json.loads(message)
        return l

    def test_b_read(self):
        return self.b.read()

    def update_user_list(self, users, view_id):
        if (self.view_id > view_id):
            #print 'old view id'
            return 

        self.lock.acquire()
        self.view_id = view_id
        for user in users:
            if user not in self.user_list:
                if user not in self.temp_user_list:
                    print user + 'not in temp user list error'
                    continue
                self.user_list[user] = self.temp_user_list[user] #copy the socket

        temp_to_delete = []
        for user in self.user_list:
            if user not in users:
                print 'remove', user, "in the user list"
                self.kicked_user_list.append(user)
                temp_to_delete.append(user)
                self.b.remove_addr(user)

        for user in temp_to_delete:
            self.kicked_user_list.append(user)
            self.user_list[user].close()
            self.user_list[user] = None
            del self.user_list[user]

        for user in users:
            if user in self.kicked_user_list:
                del self.user_list[user]

        self.lock.release()

def cast_connect(addr, uid):
    s = socket.socket()
    try:
        uid = uid.ljust(20)
        s.connect(addr)
        s.sendall(uid)
    except:
        #print 'connect error'
        return None
    return s



class LocalListener(Thread):
    def __init__(self, addr, user_list):
        Thread.__init__(self)
        self.pipe = PIPE()

        self.user_list = user_list

        self.sock = socket.socket()
        self.sock.bind(addr)
        self.sock.listen(20)

    def new_user(self):
        return self.pipe.read()

    def connect(self, addr, uid):
        s = socket.socket()
        try:
            uid = uid.ljust(20)
            s.connect(addr)
            s.sendall(uid)
        except:
            #print 'connect error'
            return None
        return s

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            try:
                user_id = conn.recv(20)
                self.user_list[user_id] = conn
                self.pipe.write(user_id)
            except:
                #print 'recv user_id error'
                continue

if __name__ == "__main__":
    import sys
    import random
    import time
    if sys.argv[1] == "l_server":
        local_addr = ("localhost", 12222)
        user_list = {}
        t_ll = LocalListener(local_addr, user_list)
        t_ll.setDaemon(True)
        t_ll.start()

        while True:
            print t_ll.new_user()
            print "list" , user_list
    if sys.argv[1] == "l_client":
        _t = {}
        user_name = sys.argv[2]
        if len(sys.argv) == 3:
            remote_server = ("localhost", 12222)
        else:
            remote_server = sys.argv[3]
        local_addr = ("localhost", random.randint(10000, 11000))
        print user_name, local_addr , "->", remote_server

        t_ll = LocalListener(local_addr, _t)
        t_ll.setDaemon(True)
        t_ll.start()

        s = t_ll.connect(remote_server, user_name)

        s.close()

        time.sleep(5)
    if sys.argv[1] == "client":
        remote_server = ("localhost", 12222)
        local_addr = ("localhost", random.randint(10000, 11000))

        user_name = sys.argv[2].ljust(20)
        t_ll = LocalListener(local_addr, {})
        s = t_ll.connect(remote_server, user_name)

        b = BroadCast()
        b.add_addr("123", s) 

        
        while True:
            #b.sendall("123")
            time.sleep(1)

    class read_pipe(Thread):
        def __init__(self, pipe):
            Thread.__init__(self)
            self.pipe = pipe
        def run(self):
            while True:
                print self.pipe.read()
        
    if sys.argv[1] == "server":
        local_addr = ("localhost", 12222)
        b = BroadCast()
        um = UserManager(b, local_addr, "tao")

        t_read_b = read_pipe(b)
        t_read_b.setDaemon(True)
        t_read_b.start()

        view_id = 0
        while True:
            users = um.new_user()
            print "before update", um.user_list.keys()
            
            try:
                del users["222".ljust(20)]
            except:
                print 'not 222'
            view_id += 1
            um.update_user_list(users, view_id)

            if len(users) > 3:
                print 'signal'
                while True:
                    print um.quit_user()
            print "after update", um.user_list.keys()
    



        
