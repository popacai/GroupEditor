'''
How to play:
first, start a TTCP server, with 'python TTCP.py server_c'
second, start several editors, with 'python lxt_self_test.py'
then, you will see the operations in several editors are identical
'''

from editor import EditorGUI
from cooperator import cooperator
import curses, time, thread, threading
from PIPE import PIPE
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

class execute_msg(threading.Thread):
    def __init__(self, read_pipe, coop):
        threading.Thread.__init__(self)
        self._pipe = read_pipe
        self._coop = coop
    def run(self):
        while True:
            msg = self._pipe.read().split(':')
            #print 'in execute_msg: ', msg
            if msg[0] == 'quit':
                break
            elif msg[0] == 'insert':
                self._coop.handle_insert(ord(msg[1]))
            elif msg[0] == 'move':
                self._coop.handle_cursor_move(int(msg[1]), int(msg[2]))
            elif msg[0] == 'delete':
                self._coop.handle_delete()
            
            coop._gui._draw()
            coop._gui._refresh_cursors()




stdscr = curses.initscr()
curses.start_color()
stdscr.bkgd(1, curses.COLOR_BLACK)
gui = EditorGUI(stdscr, '')
coop = cooperator(gui, 0, 7)
gui._cooperators.append(coop)

addr = ("192.168.1.121", 12222)
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

#recv_msg_t = recv_msg(read_pipe, write_pipe)
#recv_msg_t.start()

execute_msg_t = execute_msg(write_pipe, coop)
execute_msg_t.start()
#coop_t = coop_recv_t(coop)
#coop_t.start()

gui.main()





