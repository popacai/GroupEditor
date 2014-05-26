#!/usr/bin/python
#-*- coding: utf-8 -*-

'''
has the broadcast
addr, UID

leader:
    detect_new_user() # if a new user -> view change
    #other people. don't do it

follower:
        ignore_new_user()
    detect_quit_user() #send message to leader

'''

class Leader():
    def __init__(self):
        pass

    def view_change(self, view):
        #critical section. 
        pass
    

