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

from cooperator import cooperator
from editor import EditorGUI
import curses
import threading
from editor_manager import execute_msg


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

def init_colors():
    # init all color pairs, for cursors
    curses.start_color()
    curses.init_pair(1, 0, 7)
    curses.init_pair(2, 7, 1)
    curses.init_pair(3, 7, 2)
    curses.init_pair(4, 0, 3)
    curses.init_pair(5, 7, 4)
    curses.init_pair(6, 7, 5)
    curses.init_pair(7, 0, 6)



#20 members at most
def main():
    import hashlib

    #user_id = sys.argv[1]
    a_ip_addr = sys.argv[1]
    a_port = int(sys.argv[2])

    #user_id = hashlib.md5(str(localaddr)).hexdigest()[:20]


    #b_user_id = sys.argv[4]
    b_ip_addr = sys.argv[3]
    b_port = int(sys.argv[4])

    #Port = 10000 + index
    ip_addr = a_ip_addr
    port = a_port
    localaddr = (ip_addr, port)

    user_id = hashlib.md5(str(localaddr)).hexdigest()[:20]

    print user_id
    print localaddr

    user_id = user_id.ljust(20)

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
    if sys.argv[3] == 'n':
        um.new_group = True
    else:
        remote_ip_addr = (b_ip_addr, b_port)
        

        remote_uid = hashlib.md5(str(remote_ip_addr)).hexdigest()[:20]

        #remote_uid = b_user_id.ljust(20)

        print remote_ip_addr
        print remote_uid
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
    #ab_m.start()


    #ABCAST Reader
    t_ab_reader = read_from_abcast(ab_m)
    t_ab_reader.setDaemon(True)
    #t_ab_reader.start()

    #Init GBCAST
    gb_m = GBCASTManager(user_id,t_cast_s, um, ab_m)

    t_gbcast = Thread_GBCAST(gb_m)
    t_gbcast.setDaemon(True)
    t_gbcast.start()

    print '====================================================='
    #message 
    count = 0
    gb_m.send_user_dict_request()
    '''
    while True:
        message = raw_input()
        if (message == "sync"):
            gb_m.send_user_dict_request()
            break;
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
    '''
    while True:
        if ab_m.startFlag:
            break
        time.sleep(0.1)

    #print 'started'

    #testing code
    #while True:
    #    message = raw_input()
    #    ab_m.write(message)

    # init editor
    name = user_id
    filename = '' 
    coops = {}

    stdscr = curses.initscr()
    init_colors()
    stdscr.bkgd(1, curses.COLOR_BLACK)
    gui = EditorGUI(stdscr, name, filename)


    coop = cooperator(gui, 1)
    coops[name] = coop

    gui._cooperators.append(coop)
    gui.set_pipe(ab_m)

    execute_msg_t = execute_msg(ab_m, coops, gui)
    execute_msg_t.setDaemon(True)
    execute_msg_t.start()

    gui.main()


if __name__ == "__main__":
    main()





