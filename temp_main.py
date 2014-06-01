from ABCASTManager import ABCASTManager
from threading import Thread
from UserManager import UserManager
from BroadCast import BroadCast
from CASTSelecter import CASTSelecter

from cooperator import cooperator
from editor import EditorGUI
import curses
import threading
from editor_manager import execute_msg

from sys import argv
from PIPE import PIPE
import sys
import time

# temporary classes
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
            #print 'user_list:', self.um.fetch_user_list()
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




def main():
    user_id = sys.argv[1]
    ip_addr = "localhost"
    index = int(user_id)

    #Port = 10000 + index
    
    ip_addr = "localhost"
    port = 10000 + index
    localaddr = ('0.0.0.0', port)

    user_id = user_id.ljust(10)

    b = BroadCast()
    um = UserManager(b, localaddr, user_id)

        #Try to connect the other members
    for i in range(20):
        if i == index:
            continue #don't need to connect itself

        remote_uid = str(i).ljust(10)

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
    
    print '====================================================='

    #Init ABCASTManager
    am = ABCASTManager(user_id, t_cast_s, um)
   
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

    gui.set_pipe(am)
    execute_msg_t = execute_msg(am, coops, gui)
    execute_msg_t.start()

    am.start()

    #Code from Tao
    #Daemon threading for keeping adding the users 
    am.addUser("321") #call for update
    print 'user_list', um.fetch_user_list()
    
    ua = user_add(um, am)
    ua.setDaemon(True)
    
    

    ua.start()
    #auto UserManager update user list
    #message 
    '''
    while True:
        message = raw_input()
        if (message == ""):
            continue
        #t_cast_s.sendCB(message)
        am.write(message)
    '''
 
    #Init recvCB()
    #t_cb_recv = Thread_recvCB(t_cast_s)
    #t_cb_recv.setDaemon(True)
    #t_cb_recv.start()
    #t_ab_reader = read_from_abcast(am)
    #t_ab_reader.setDaemon(True)
    #t_ab_reader.start()

    gui.main()


if __name__ == "__main__":
    main()


