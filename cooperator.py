
import curses
class cooperator:

    def __init__(self, gui, identifer):
        self._gui = gui
        self._id = identifer
        self._row = 0
        self._col = 0
        self._pipe = None

    def set_pipe(self, pipe):
        self._pipe = pipe

    def handle_insert(self, char):

        if char == ord('\n'): # return
            if self._gui.insert(char, self._row, self._col):
                self._gui.move_cursor(self._row, self._col, self._row + 1, 0) 
                self._row += 1
                self._col = 0
                self._gui._refresh_cursors()
                return True
            else:
                self._gui._refresh_cursors()
                return False

        elif char == 127: #backspace

            if self._row == 0 and self._col == 0:
                return True # no effect
            else:
                (dest_row, dest_col) = self._gui.backspace(self._row, self._col)
                self._row = dest_row
                self._col = dest_col
                self._gui._refresh_cursors()
                return True
        else: # normal input
            if self._gui.insert(char, self._row, self._col):
                self.handle_cursor_move(0,1)
                return True
            else:
                return False

    def handle_cursor_move(self, row_offset, col_offset):
        self._row, self._col = self._gui.move_cursor(self._row, self._col, self._row + row_offset, self._col + col_offset)
        self._gui._refresh_cursors()


    def handle_delete(self):
        self._gui.delete(self._row, self._col)	
        self._gui._refresh_cursors()

    def get_para(self):
        return self._row, self._col
