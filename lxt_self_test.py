from editor import EditorGUI
from cooperator import cooperator
import curses, time, thread, threading
from pipe import PIPE
from TTCP import *
import socket

class recv_msg(threading.Thread):
    def __init__(self, read_pipe, write_pipe):
        threading.Thread.__init__(self)
        self._read_pipe = read_pipe
        self._write_pipe = write_pipe
    def run(self):
        while True:
            msg = self._read_pipe.read()
            #print 'manager received: ',msg
            self._write_pipe.write(msg)

class coop_recv_t(threading.Thread):
    def __init__(self, coop):
        threading.Thread.__init__(self)
        self._coop = coop
    def run(self):
        self._coop.recv_message()




stdscr = curses.initscr()
curses.start_color()
stdscr.bkgd(1, curses.COLOR_BLACK)
gui = EditorGUI(stdscr, '')
coop = cooperator(gui, 0, 7)
gui._cooperators.append(coop)

addr = ("localhost", 10003)
s = socket.socket()
s.connect(addr)

signal_pipe = PIPE()
output_pipe = PIPE()
input_pipe = PIPE()

'''
#t_signal = read_pipe(signal_pipe)
#t_output = read_pipe(output_pipe)
t_signal.setDaemon(True)
t_output.setDaemon(True)
t_signal.start()
t_output.start()
'''

t1 = TSTCP(s, addr, input_pipe, signal_pipe)
t1.setDaemon(True)
t1.start()

t2 = TRTCP(s, addr, output_pipe, signal_pipe)
t2.setDaemon(True)
t2.start()


read_pipe = input_pipe
write_pipe = output_pipe
gui.set_pipe(read_pipe)
coop.set_pipe(write_pipe)

recv_msg_t = recv_msg(read_pipe, write_pipe)
recv_msg_t.start()

coop_t = coop_recv_t(coop)
coop_t.start()

gui.main()





