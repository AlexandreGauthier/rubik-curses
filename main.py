# import rpdb2; rpdb2.start_embedded_debugger("123123")
from curses import wrapper
from random import choice
from copy import deepcopy
import curses

defaultState = [[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
                [[2, 2, 2], [2, 2, 2], [2, 2, 2]],
                [[3, 3, 3], [3, 3, 3], [3, 3, 3]],
                [[4, 4, 4], [4, 4, 4], [4, 4, 4]],
                [[5, 5, 5], [5, 5, 5], [5, 5, 5]]]

rotatekeys = {"a": ["left"], "A": ["Left"],
              "s": ["right"], "S": ["Right"],
              "d": ["up"], "D": ["Up"],
              "f": ["down"], "F": ["Down"],
              "z": ["front"], "Z": ["Front"],
              "x": ["back"], "X": ["Back"],
              "q": [], "Q": []}

class Cube:
    def __init__(self, state):
        self.state = state

    def move(self, move):
        changemap = {"up": [[4, 1, 0, 3, 5, 2], 1, 3],  # 0 -> Which sides go where. 1 -> Which side rotates counterclockwise
                     "down": [[2, 1, 5, 3, 0, 4], 3, 1],  # 2 -> Which side rotates clockwise
                     "right": [[1, 5, 2, 0, 4, 3], 2, 4],
                     "left": [[3, 0, 2, 5, 4, 1], 4, 2]}
        if move in changemap:
            self.state = [self.state[i] for i in changemap[move][0]]
            self.state[changemap[move][1]] = rotate_matrix_counterclockwise(self.state[changemap[move][1]])
            self.state[changemap[move][2]] = rotate_matrix_clockwise(self.state[changemap[move][2]])


    def shuffle(self):
        rotatemoves = ["left", "Left", "right", "Right", "front", "Front", "back", "Back", "Up", "up", "Down", "Down"]
        for n in range(50):
            self.rotate([choice(rotatemoves)])

    def rotate(self, moves):
        mirror = {"left": "right", "right": "left", "up": "down", "down": "up"}

        for move in moves:
            if move.lower() == "back":
                self.move("right")
                self.move("right")

                if move.islower():
                    self.rotate(["front"])
                else:
                    self.rotate(["Front"])

                self.move("left")
                self.move("left")

                return 0

            if move.lower() in mirror:
                self.move(mirror[move.lower()])

            oldstate = deepcopy(self.state)

            if move.islower():
                self.state[0] = rotate_matrix_clockwise(self.state[0])

                for n in range(3):
                    self.state[2][2][n] = oldstate[1][2-n][2]
                    self.state[1][n][2] = oldstate[4][0][n]
                    self.state[4][0][n] = oldstate[3][2-n][0]
                    self.state[3][n][0] = oldstate[2][2][n]

            else:
                self.state[0] = rotate_matrix_counterclockwise(self.state[0])

                for n in range(3):
                    self.state[1][2-n][2] = oldstate[2][2][n]
                    self.state[4][0][n] = oldstate[1][n][2]
                    self.state[3][2-n][0] = oldstate[4][0][n]
                    self.state[2][2][n] = oldstate[3][n][0]

            if move.lower() in mirror:
                self.move(move.lower())


def parse_key(key, cube, rotatekeys):
    movekeys = {"KEY_UP": "up",
                "KEY_DOWN": "down",
                "KEY_RIGHT": "right",
                "KEY_LEFT": "left"}

    if key in movekeys:
        cube.move(movekeys[key])

    if key in rotatekeys:
        cube.rotate(rotatekeys[key])
    if key == "L":
        return 1
    if key == "P":
        cube.shuffle()

    return 0


def rotate_matrix_clockwise(matrix):
    return [list(a) for a in zip(*matrix[::-1])]


def rotate_matrix_counterclockwise(matrix):
    return [list(a) for a in zip(*matrix)[::-1]]


def draw(stdscr, cube):
    stdscr.addstr(0, 0, "RUBIK 0.01", curses.color_pair(100+cube[0][1][1]))
    offset = (4, 2)

    squaresize = (1, 2)
    
    sideoffsets = [(1, 1), (1, 0), (0, 1), (1, 4), (4, 1)]

    realoffsets = []

    for y, x in sideoffsets:
        realoffsets.append((y*squaresize[0]*3, x*squaresize[1]*3))
    
    longsides = [0, 2, 4]
    tallsides = [0, 1, 3]

    for sidenb, side in enumerate(cube[:-1]):
        
        if sidenb in longsides:
            xmultiplier = squaresize[1]*3
        else:
            xmultiplier = squaresize[1]
        if sidenb in tallsides:
            ymultiplier = squaresize[0]*3
        else:
            ymultiplier = squaresize[0]
        
        for linenb, line in enumerate(side):
            for squarenb, color in enumerate(line):

                for n in range(ymultiplier):
                    stdscr.addstr(
                        offset[0]+realoffsets[sidenb][0]+linenb*ymultiplier+n,
                        offset[1]+realoffsets[sidenb][1]+squarenb*xmultiplier,
                        " "*xmultiplier, curses.color_pair(100+color))

    for n, text in enumerate(open("instructions_moving.txt").readlines()):
        stdscr.addstr(offset[0]+n, 40, text, curses.A_STANDOUT if text.isupper() else curses.A_NORMAL)


    stdscr.refresh()
                
def main(stdscr):
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    cube = Cube(defaultState)
    nextkey = ""
    curses.curs_set(False)

    if curses.can_change_color():
        curses.init_color(curses.COLOR_RED, 769, 118, 227)
        curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
        curses.init_color(curses.COLOR_BLUE, 0, 318, 729)
        curses.init_color(curses.COLOR_GREEN, 0, 620, 376)
        curses.init_color(curses.COLOR_YELLOW, 1000, 835, 0)
        curses.init_color(curses.COLOR_MAGENTA, 1000, 345, 0)  # Orange

    curses.init_pair(100, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(101, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(102, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(103, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(104, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(105, curses.COLOR_BLACK, curses.COLOR_MAGENTA)  # Is magenta if curses.can_change_colors()=false

    while True:
        stdscr.clear()

        if parse_key(nextkey, cube, rotatekeys):
            return 0
        draw(stdscr, cube.state)
        nextkey = stdscr.getkey()


wrapper(main)
