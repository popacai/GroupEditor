#!/usr/bin/python
#-*- coding: utf-8 -*-


from threading import Thread
import socket

#Group_every_list

'''
Group:
    Listen()
    if someone has connect to this
        uid = sock.recv(1500)
        self.uid_list[uid] = sock
        self.uid_pipe.write(uid)
Client:
    connect_group(self, uid, addr)
    sock = socket.connect(addr)
    sock.sendall(self.uid)
    self.uid_list[uid] = sock

'''
class GroupManager():
    def __init__(self, uid):
        self.uid_pipe = PIPE()
        self.uid_list = {}
        self.uid = uid

        self.CM = ConnectionManager(self.uid_list, self.uid_pipe)
        self.BC = BroadCast()

        self.CM.setDaemon(True)
        self.CM.start()

    def add_user(self, uid, addr):
        self.CM.connect_group(uid, addr)
    
    def new_user_found(self):
        return self.uid_pipe.read()

class ConnectionManager(Thread):
    """Manager for sending ABCAST"""
    def __init__(self, uid, uid_list, uid_pipe):
        self.uid = uid
        self.uid_list = uid_list
        self.sock = socket.socket()
        self.uid_pipe = uid_pipe
        Thread.__init__(self)

    def listen(self, addr):
        self.sock.listen(addr)

    def run(self):
        while True:
            client_sock = self.sock.accept()
            remote_uid = sock.recv(1500)
            self.uid_list[remote_uid] = client_sock
            self.uid_pipe.write(remote_uid)

    def connect_group(self, uid, addr):
        client_sock = socket.socket()
        client_sock.connect(addr)
        client_sock.sendall(self.uid)
        self.uid_list[uid] = client_sock


if __name__ == '__main__':
    pass
