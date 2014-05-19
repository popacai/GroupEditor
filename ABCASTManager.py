#!/usr/bin/python
#-*- coding: utf-8 -*-
import PIPE


class ABCASTManager(object):
    """Manager for sending ABCAST"""
    def __init__(self, addr):
        super(ABCASTManager, self).__init__()
        self.inputPipe = PIPE()
        self.outputPipe = PIPE()
        self.addr = addr
        self.clientList = []

    def read(self):
        pass

    def write(self, message):
        pass

    def quit(self):
        pass


if __name__ == '__main__':
    pass
