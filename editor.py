"""Simple curses-based text editor."""

from contextlib import contextmanager
from sys import argv
import curses
import os
from PIPE import PIPE


class Buffer(object):
    """The basic data structure for editable text.

    The buffer is column and row oriented. Column and row numbers start with 0.
    A buffer always has at least one row. All positions within a buffer specify
    a position between characters.
    """

    def __init__(self, text=''):
        """Create a new Buffer, optionally initialized with text."""
        self._lines = text.split('\n')

    def get_lines(self):
        """Return list of lines in the buffer."""
        return list(self._lines) # return a copy

    def _check_point(self, row, col):
        """Raise ValueError if the given row and col are not a valid point."""
        if row < 0 or row > len(self._lines) - 1:
            raise ValueError("Invalid row: '{}'".format(row))
        cur_row = self._lines[row]
        if col < 0 or col > len(cur_row):
            raise ValueError("Invalid col: '{}'".format(col))

    def set_text(self, row1, col1, row2, col2, text):
        """Set the text in the given range.

        The end of the range is exclusive (to allow inserting text without
        removing a single character). Column numbers are positions between
        characters.

        Raises ValueError if the range is invalid.
        """
        # TODO check that point2 is after or the same as point1
        self._check_point(row1, col1)
        self._check_point(row2, col2)

        line = self._lines[row1][:col1] + text + self._lines[row2][col2:]
        self._lines[row1:row2+1] = line.split('\n')
    
    def get_text(self, row, col):
        if row < 0 or row > len(self._lines) - 1:
            return ' '		
        if col < 0 or col > len(self._lines[row]) - 1:
            return ' '
        return self._lines[row][col]


class EditorGUI(object):

    def __init__(self, stdscr, username, filename):
        """Create the GUI with curses screen and optional filename to load."""
        self._stdscr = stdscr
        self._COLOR_NUM = 7
        self._username = username

        self._COL_MAX = 50
        self._ROW_MAX = 20 

        # if filename already exists, try to load from it
        text = ''
        if filename != None and os.path.isfile(filename):
            with open(filename) as f:
                text = f.read()

        self._filename = filename
        self._buf = Buffer(text)
        self._row = 0
        self._col = 0
        self._scroll_top = 0 # the first line number in the window
        self._mode = 'normal'
        self._message = ''
        self._will_exit = False

        self._pipe = None
        self._cooperators = []

        curses.curs_set(0)

    def set_pipe(self, pipe):
        self._pipe = pipe
        self._pipe.write(self._username + '__join') # indicate that i am coming

    def add_cooperator(self, coop):
        self._cooperators.append(coop)

    def _draw_gutter(self, num_start, num_rows, last_line_num):
        """Draw the gutter, and return the gutter width."""
        line_nums = range(num_start, num_start + num_rows)
        assert len(line_nums) == num_rows
        gutter_width = max(3, len(str(last_line_num))) + 1
        for y, line_num in enumerate(line_nums):
            if line_num > last_line_num:
                text = '~'.ljust(gutter_width)
            else:
                text = '{} '.format(line_num).rjust(gutter_width)
            self._stdscr.addstr(y, 0, text, curses.A_REVERSE)
        return gutter_width

    def _draw(self):
        """Draw the GUI."""
        self._stdscr.clear()
        height = self._stdscr.getmaxyx()[0]
        width = self._stdscr.getmaxyx()[1]
        self._draw_status_line(0, height - 1, width)
        self._draw_text(0, 0, width, height - 1)
        self._stdscr.refresh()

    def _draw_status_line(self, left, top, width):
        """Draw the status line."""
        # TODO: can't write to bottom right cell
        mode = '{} {}'.format(self._mode.upper(),
                              self._message).ljust(width - 1)
        self._stdscr.addstr(top, left, mode, curses.A_REVERSE)
        position = 'LN {}:{} '.format(self._row + 1, self._col + 1)
        self._stdscr.addstr(top, left + width - 1 - len(position), position,
                            curses.A_REVERSE)

    def _get_num_wrapped_lines(self, line_num, width):
        """Return the number of lines the given line number wraps to."""
        return len(self._get_wrapped_lines(line_num, width))

    def _get_wrapped_lines(self, line_num, width, convert_nonprinting=True):
        """Return the wrapped lines for the given line number."""
        def wrap_text(text, width):
            """Wrap string text into list of strings."""
            if text == '':
                yield ''
            else:
                for i in xrange(0, len(text), width):
                    yield text[i:i + width]
        assert line_num >= 0, 'line_num must be > 0'
        line = self._buf.get_lines()[line_num]
        if convert_nonprinting:
            line = self._convert_nonprinting(line)
        return list(wrap_text(line, width))

    def _scroll_bottom_to_top(self, bottom, width, height):
        """Return the first visible line's number so bottom line is visible."""
        def verify(top):
            """Verify the result of the parent function is correct."""
            rows = [list(self._get_wrapped_lines(n, width))
                    for n in range(top, bottom + 1)]
            num_rows = sum(len(r) for r in rows)
            assert top <= bottom, ('top line {} may not be below bottom {}'
                                   .format(top, bottom))
            assert num_rows <= height, (
                '{} rows between {} and {}, but only {} remaining. rows are {}'
                .format(num_rows, top, bottom, height, rows))

        top, next_top = bottom, bottom
        # distance in number of lines between top and bottom
        distance = self._get_num_wrapped_lines(bottom, width)

        # move top upwards as far as possible
        while next_top >= 0 and distance <= height:
            top = next_top
            next_top -= 1
            distance += self._get_num_wrapped_lines(max(0, next_top), width)

        verify(top)
        return top

    def _scroll_to(self, line_num, width, row_height):
        """Scroll so the line with the given number is visible."""
        # lowest scroll top that would still keep line_num visible
        lowest_top = self._scroll_bottom_to_top(line_num, width, row_height)

        if line_num < self._scroll_top:
            # scroll up until line_num is visible
            self._scroll_top = line_num
        elif self._scroll_top < lowest_top:
            # scroll down to until line_num is visible
            self._scroll_top = lowest_top

    @staticmethod
    def _convert_nonprinting(text):
        """Replace nonprinting character in text."""
        # TODO: it would be nice if these could be highlighted when displayed
        res = []
        for char in text:
            i = ord(char)
            if char == '\t':
                res.append('->  ')
            elif i < 32 or i > 126:
                res.append('<{}>'.format(hex(i)[2:]))
            else:
                res.append(char)
        return ''.join(res)

    def _draw_text(self, left, top, width, height):
        """Draw the text area."""
        # TODO: handle single lines that occupy the entire window
        highest_line_num = len(self._buf.get_lines())
        gutter_width = max(3, len(str(highest_line_num))) + 1
        line_width = width - gutter_width # width to which text is wrapped
        cursor_y, cursor_x = None, None # where the cursor will be drawn

        # set scroll_top so the cursor is visible
        self._scroll_to(self._row, line_width, height)

        line_nums = range(self._scroll_top, highest_line_num)
        cur_y = top
        trailing_char = '~'

        for line_num in line_nums:

            # if there are no more rows left, break
            num_remaining_rows = top + height - cur_y
            if num_remaining_rows == 0:
                break

            # if all the wrapped lines can't fit on screen, break
            wrapped_lines = self._get_wrapped_lines(line_num, line_width)
            if len(wrapped_lines) > num_remaining_rows:
                trailing_char = '@'
                break

            # calculate cursor position if cursor must be on this line
            if line_num == self._row:
                lines = self._get_wrapped_lines(line_num, line_width,
                                                convert_nonprinting=False)
                real_col = len(self._convert_nonprinting(
                    ''.join(lines)[:self._col])
                )
                cursor_y = cur_y + real_col / line_width
                cursor_x = left + gutter_width + real_col % line_width

            # draw all the wrapped lines
            for n, wrapped_line in enumerate(wrapped_lines):
                if n == 0:
                    gutter = '{} '.format(line_num + 1).rjust(gutter_width)
                else:
                    gutter = ' ' * gutter_width
                self._stdscr.addstr(cur_y, left, gutter, curses.A_REVERSE)
                self._stdscr.addstr(cur_y, left + len(gutter), wrapped_line)
                cur_y += 1

        # draw empty lines
        for cur_y in range(cur_y, top + height):
            gutter = trailing_char.ljust(gutter_width)
            self._stdscr.addstr(cur_y, left, gutter)

        # position the cursor
        assert cursor_x != None and cursor_y != None
        self._stdscr.move(cursor_y + 0, cursor_x + 0)
	
    def _refresh_cursors(self):
        #self._draw()
        highest_line_num = len(self._buf.get_lines())
        gutter_width = max(3, len(str(highest_line_num))) + 1
        for coop in self._cooperators: # refresh all cursors
            #self._cooperators[i].handle_cursor_move(0, 0)
            #print 'refresh'
            row = coop._row
            col = coop._col
            #curses.init_pair(8, 3, 5)
            #self._stdscr.addstr(row, col + gutter_width, self._buf.get_text(row, col), curses.color_pair(coop._id / self._COLOR_NUM))
            #print 'refresh'
            #print coop._id % self._COLOR_NUM
            self._stdscr.addstr(row, col + gutter_width, self._buf.get_text(row, col), curses.color_pair(coop._id % self._COLOR_NUM))
            self._stdscr.refresh()

    def _check_cursor(self, row, col):
        if row < 0:
            row = 0
        if row > len(self._buf._lines) - 1:
            row = len(self._buf._lines) - 1
        if col < 0:
            col = 0
            #print 'ROW is : %d                           \n\n\n'%row
        if col > len(self._buf._lines[row]):
            col = len(self._buf._lines[row])
        return (row, col)
    def _handle_normal_keypress(self, char):
        """Handle a keypress in normal mode."""
        #print len(char)
        #if char == [27, 91, 65]:
        #    print 'up!!!'
        if char == ord('q'): # quit
            self._will_exit = True
            self._pipe.write(self._username + '__quit')
        elif char == ord('j'): # down
            self._pipe.write(self._username + '__move__1__0')
            #self._row += 1
        elif char == ord('k'): # up 
            self._pipe.write(self._username + '__move__-1__0')
            #self._row -= 1
        elif char == ord('h'): # left
            self._pipe.write(self._username + '__move__0__-1')
            #self._col -= 1
        elif char == ord('l'): # right
            self._pipe.write(self._username + '__move__0__1')
            #self._col += 1

        elif char == ord('x'): # delete a character
            self._pipe.write(self._username + '__delete')
            #self._buf.set_text(self._row, self._col, self._row,
                                #self._col + 1, '')
        elif char == ord('i'): # enter insert mode
            self._mode = "insert"
        elif char == ord('a'): # enter insert mode after cursor
            self._mode = "insert"
            self._pipe.write(self._username + '__move__0__1')
            #self._col += 1
            """ 
        elif char == ord('o'): # insert line after current
            cur_line_len = len(self._buf.get_lines()[self._row])
            self._buf.set_text(self._row, cur_line_len, self._row,
                               cur_line_len, '\n')
            self._row += 1
            self._col = 0
            self._mode = "insert"
        elif char == ord('O'): # insert line before current
            self._buf.set_text(self._row, 0, self._row, 0, '\n')
            self._col = 0
            self._mode = "insert"
            """ 
        elif char == ord('w'): # write file
            if self._filename == None:
                self._message = 'Can\'t write file without filename.'
            else:
                try:
                    with open(self._filename, 'w') as f:
                        f.write('\n'.join(self._buf.get_lines()))
                except IOError as e:
                    self._message = ('Failed to write file \'{}\': {}'
                                     .format(self._filename, e))
        else:
            self._message = 'Unknown key: {}'.format(char)

    def _handle_insert_keypress(self, char):
        """Handle a keypress in insert mode."""
        if char == curses.KEY_UP:
            self._pipe.write(self._username + '__move__-1__0')

        elif char == curses.KEY_DOWN:
            self._pipe.write(self._username + '__move__1__0')

        elif char == curses.KEY_LEFT:
            self._pipe.write(self._username + '__move__0__-1')

        elif char == curses.KEY_RIGHT:
            self._pipe.write(self._username + '__move__0__1')

        elif char == 27:
            # leaving insert mode moves cursor left
            if self._mode == 'insert':
                self._pipe.write(self._username + '__move__0__-1')
                #self._col -= 1
            self._mode = "normal"
        elif char == 263: # backspace
            self._pipe.write(self._username + '__insert__' + chr(127))
            """ 
            if self._col == 0 and self._row == 0:
                pass # no effect
            elif self._col == 0:
                # join the current line with the previous one
                prev_line = self._buf.get_lines()[self._row - 1]
                cur_line = self._buf.get_lines()[self._row]
                self._buf.set_text(self._row - 1, 0, self._row,
                                    len(cur_line), prev_line + cur_line)
                self._col = len(prev_line)
                self._row -= 1
            else:
                # remove the previous character
                self._buf.set_text(self._row, self._col - 1, self._row,
                                    self._col, '')
                self._col -= 1
            """ 
        elif char < 256:
            self._pipe.write(self._username + '__insert__'+chr(char))
        """ 
            self._message = ('inserted {} at row {} col {}'
                             .format(char, self._row, self._col))
            self._buf.set_text(self._row, self._col, self._row,
                                self._col, chr(char))
            if chr(char) == '\n':
                self._row += 1
                self._col = 0
            else:
                self._col += 1
        """ 

    def move_cursor(self, curr_row, curr_col, dest_row, dest_col):
        #curses.start_color()
        highest_line_num = len(self._buf.get_lines())
        gutter_width = max(3, len(str(highest_line_num))) + 1
        self._stdscr.addstr(curr_row, curr_col + gutter_width, self._buf.get_text(curr_row, curr_col), curses.color_pair(0)) #cancel previous cursor
        #curses.init_pair(8, front_color, back_color)
        dest_row, dest_col = self._check_cursor(dest_row, dest_col)
        #self._stdscr.addstr(dest_row, dest_col + gutter_width, self._buf.get_text(dest_row, dest_col), curses.color_pair(8)) # add new cursor
        #self._stdscr.refresh()
        #print 'set: ', dest_row, dest_col
        self._stdscr.refresh()

        return (dest_row, dest_col)

    def insert(self, char, row, col):
        #print 'in insert: ', char
        max_width = min(self._stdscr.getmaxyx()[1] - 10, self._COL_MAX)
        max_height = min(self._stdscr.getmaxyx()[0] - 3, self._ROW_MAX)
        if len(self._buf.get_lines()[row]) > max_width and char != ord('\n'):
            #print 'rrrrrrrrrow: ', row
            return False
        elif len(self._buf.get_lines()) > max_height and char == ord('\n'):
            return False
        row, col = self._check_cursor(row, col)
        self._buf.set_text(row, col, row, col, chr(char))
        return True 
        #self._draw()
        # TODO refresh all cursors

    def backspace(self, row, col):
        highest_line_num = len(self._buf.get_lines())
        gutter_width = max(3, len(str(highest_line_num))) + 1
        self._stdscr.addstr(row, col + gutter_width, self._buf.get_text(row, col)) #cancel previous cursor

        if col == 0:
            # join the current line with the previous one
            prev_line = self._buf.get_lines()[row - 1]
            cur_line = self._buf.get_lines()[row]
            self._buf.set_text(row - 1, 0, row, len(cur_line), prev_line + cur_line)
            col = len(prev_line)
            row -= 1
            row, col = self._check_cursor(row, col)
            #deal with the cursor
            #self._stdscr.addstr(row, col + gutter_width, cur_line + ' ')
            #self._draw()
            #self._stdscr.addstr(row, col + gutter_width, cur_line[0], curses.color_pair(1))
            # TODO refresh all cursors
            #self._stdscr.refresh()
        else:
            # remove the previous character
            self._buf.set_text(row, col - 1, row, col, '')
            col -= 1
            #deal with the cursor
            curr_line = self._buf.get_lines()[row][col:]
            #self._stdscr.addstr(row, col + gutter_width, curr_line + ' ')
            #self._draw()
            #self._stdscr.addstr(row, col + gutter_width, curr_line[0], curses.color_pair(1))
            # TODO refresh all cursors
            #self._stdscr.refresh()

        return (row, col)

    def delete(self, row, col):
        highest_line_num = len(self._buf.get_lines())
        gutter_width = max(3, len(str(highest_line_num))) + 1
        new_row, new_col = self._check_cursor(row, col + 1)
        self._buf.set_text(row, col, new_row, new_col, '')
        #self._draw()
        #self._stdscr.addstr(row, col + gutter_width, self._buf.get_text(row, col), curses.color_pair(1))
        #self._stdscr.refresh()
        # TODO refresh all cursors

    def main(self):
        """GUI main loop."""
        self._draw()
        self._message = ''
        self._stdscr.keypad(1)
        while not self._will_exit:

            #print 'hello?'
            char = self._stdscr.getch()
            #print char
            #if char == curses.KEY_UP:
            #    self.
            #elif char != -1:
            #print char
            if self._mode == 'normal':
                if char == curses.KEY_UP:
                    self._handle_normal_keypress(ord('k'))
                elif char == curses.KEY_DOWN:
                    self._handle_normal_keypress(ord('j'))
                elif char == curses.KEY_LEFT:
                    self._handle_normal_keypress(ord('h'))
                elif char == curses.KEY_RIGHT:
                    self._handle_normal_keypress(ord('l'))
                elif char < 256:
                    self._handle_normal_keypress(char)
            elif self._mode == 'insert':
                self._handle_insert_keypress(char)

            # TODO: get rid of this position clipping
            num_lines = len(self._buf.get_lines())
            self._row = min(num_lines - 1, max(0, self._row))
            # on empty lines, still allow col 1
            num_cols = max(1, len(self._buf.get_lines()[self._row]))
            # in insert mode, allow using append after the last char
            if self._mode == 'insert':
                num_cols += 1
            self._col = min(num_cols - 1, max(0, self._col))

            #self._draw()
            self._draw()
            self._refresh_cursors()
            #self._stdscr.refresh()
            #print 'main'
            self._message = ''

        # out of while, close the curses window 
        curses.nocbreak()
        self._stdscr.keypad(0)
        curses.echo()
        curses.endwin()




@contextmanager
def use_curses():
    """Context manager to set up and tear down curses."""
    stdscr = curses.initscr()
    curses.noecho() # do not echo keys
    curses.cbreak() # don't wait for enter
    try:
        yield stdscr
    finally:
        # clean up and exit
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()


def curses_main():
    """Start the curses GUI."""
    filename = argv[1] if len(argv) > 1 else None
    with use_curses() as stdscr:
        gui = EditorGUI(stdscr, filename)
        gui.main()


if __name__ == '__main__':
    curses_main()
