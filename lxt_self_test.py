from editor import EditorGUI
from cooperator import cooperator
from sys import argv
import curses, time, thread, threading
from pipe import PIPE
from TTCP import *
import socket

'''
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
'''

class execute_msg(threading.Thread):
    def __init__(self, read_pipe, coops, gui):
        threading.Thread.__init__(self)
        self._pipe = read_pipe
        self._coops = coops
        self._gui = gui
    def run(self):
        while True:
            msg = self._pipe.read().split('__')
            if msg[0] not in coops:
                # add new cooperators
                #print '???'
                identifer = len(self._coops) + 1
                new_coop = cooperator(self._gui, identifer)
                self._coops[msg[0]] = new_coop
                gui._cooperators.append(new_coop)
                self._gui._pipe.write(self._gui._username + '__exits')

            coop = self._coops[msg[0]]
            #print 'in execute_msg: ', msg
            if msg[1] == 'quit':
                break
            elif msg[1] == 'insert':
                ori_row, ori_col = coop.get_para()
                if coop.handle_insert(ord(msg[2])):
                    #if msg[2] == chr(127):
                        #print 'update'
                        #TODO what the fuck???
                    self.update_cursors(ori_row, ori_col, msg)

            elif msg[1] == 'move':
                coop.handle_cursor_move(int(msg[2]), int(msg[3]))
            elif msg[1] == 'delete':
                ori_row, ori_col = coop.get_para()
                coop.handle_delete()
                self.update_cursors(ori_row, ori_col, msg)
                #print '???'
            
            coop._gui._draw()
            coop._gui._refresh_cursors()

    def update_cursors(self, ori_row, ori_col, msg):
        if msg[1] == 'insert' and msg[2] != '\n' and msg[2] != chr(127):
            for name, coop in self._coops.iteritems():
                #print '!!!'
                if name != msg[0]:
                    #print '???'
                    coop_row, coop_col = coop.get_para()
                    if coop_row == ori_row and coop_col >= ori_row:
                        coop.handle_cursor_move(0,1)
        elif msg[1] == 'insert' and msg[2] == '\n':
            for name, coop in self._coops.iteritems():
                if name != msg[0]:
                    coop_row, coop_col = coop.get_para()
                    if coop_row > ori_row:
                        coop.handle_cursor_move(1,0)
                    elif coop_row == ori_row:
                        coop.handle_cursor_move(1, 0 - len(self._gui._buf.get_lines()[ori_row]))
            
        elif (msg[1] == 'delete' or (msg[1] == 'insert' and msg[2] == chr(127))) and ori_col > 0:
            #print '!!!'
            for name, coop in self._coops.iteritems():
                if name != msg[0]:
                    coop_row, coop_col = coop.get_para()
                    #print '!!!'
                    if coop_row == ori_row and coop_col >= ori_col:
                        coop.handle_cursor_move(0, -1)

        elif (msg[1] == 'delete' or (msg[1] == 'insert' and msg[2] == chr(127))) and ori_col == 0:
            #print '!!!'
            for name, coop in self._coops.iteritems():
                if name != msg[0]:
                    coop_row, coop_col = coop.get_para()
                    #print '???'
                    if coop_row > ori_row:
                        coop.handle_cursor_move(-1, 0)



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


if __name__ == '__main__':
    
    name = argv[1]
    filename = argv[2]
    coops = {}

    stdscr = curses.initscr()
    init_colors()
    stdscr.bkgd(1, curses.COLOR_BLACK)
    gui = EditorGUI(stdscr, name, filename)


    coop = cooperator(gui, 1)
    coops[name] = coop
    gui._cooperators.append(coop)
    # TODO gui._cooperators.append(cooperator(gui, 1))
	#gui._cooperators.append(cooperator(gui, 2))
	#gui._cooperators.append(cooperator(gui, 3))

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

    #recv_msg_t = recv_msg(read_pipe, write_pipe)
    #recv_msg_t.start()

    execute_msg_t = execute_msg(write_pipe, coops, gui)
    execute_msg_t.start()
    #coop_t = coop_recv_t(coop)
    #coop_t.start()

    gui.main()


