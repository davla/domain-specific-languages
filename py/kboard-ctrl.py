#!/usr/bin/env python

import curses
import glib
import sys

from thymioII import ThymioII

class ControlledThymio(ThymioII):
    direction_chooser = {
        'up': {
            'left': ('left', 90),
            'down': ('left', 180),
            'right': ('right', 90)
        },
        
        'left': {
            'up': ('right', 90),
            'down': ('left', 90),
            'right': ('right', 180)
        },

        'down': {
            'left': ('right', 90),
            'up': ('left', 180),
            'right': ('left', 90)
        },

        'right': {
            'left': ('right', 180),
            'up': ('left', 90),
            'down': ('left', 90)
        }
    }

    def __init__(self, name):
        super(ControlledThymio, self).__init__(name)

        self.current_direction = 'up'

    def cmd(self, cmd):
        if self.current_direction == cmd:
            return

        data = ControlledThymio.direction_chooser \
                [self.current_direction][cmd]
        self._turn(data[0], data[1])

def main(name='thymio-II'):

    speed = 300
    robot = ControlledThymio(name)
    
    robot.move_forward(300)
    robot.cmd('left')
    robot.run()
        
if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except IndexError:
        main()
