import dbus
import sys
import time
import math
import traceback
import glib
from os import path

from dbus.mainloop.glib import DBusGMainLoop
import gobject
# required to prevent the glib main loop to interfere with Python threads
gobject.threads_init()
dbus.mainloop.glib.threads_init()

from aseba import Aseba, AsebaException

class ThymioII(Aseba):
    wheel_distance = 9 # cm
    threshold = 500
    big_angle = 90
    small_angle = 30

    turn_decider = [
        # Far left
        lambda robot: robot.turn_right(ThymioII.small_angle),
            
        # Middle left
        lambda robot: robot.turn_right(ThymioII.big_angle),

        # Middle
        lambda robot: robot.u_turn(),

        # Middle right
        lambda robot: robot.turn_left(ThymioII.big_angle),

        # Far right
        lambda robot: robot.turn_left(ThymioII.small_angle)
    ]
    
    def __init__(self, name):
        Aseba.__init__(self)

        nodes = self.network.GetNodesList()
        if name not in nodes:
            nodes = map(str, list(nodes))
            raise AsebaException("Cannot find node {nodeName}! "
                                 "These are the available nodes: {nodes}" \
                                 .format(nodeName=name, nodes=list(nodes)))
        self.name = name
        self.desired_speed = 0

    def __enter__():
        pass

    def move_forward(self, speed):
        self.desired_speed = speed
        self.network.SetVariable(self.name, 'motor.left.target', [speed])
        self.network.SetVariable(self.name, 'motor.right.target', [speed])

    def stop(self):
        self.move_forward(0)

    def _turn(self, direction, deg):
        radians = math.pi * deg / 180
        speed = self.network.GetVariable(self.name,
                'motor.{dir}.speed'.format(dir=direction))

        cms_speed = speed[0] * 20 / 500 * 0.75
        if cms_speed <= 0:
            return
        
        time_stop = ThymioII.wheel_distance * radians / cms_speed
        self.network.SetVariable(self.name,
                'motor.{dir}.target'.format(dir=direction),
                [0])
        time.sleep(time_stop)
        self.move_forward(self.desired_speed)

    def turn_left(self, deg):
        self._turn('left', deg)

    def turn_right(self, deg):
        self._turn('right', deg)

    def u_turn(self):
        self._turn('right', 180)

    def check_prox(self):
        prox_sensors = self.network.GetVariable(self.name,
                                                'prox.horizontal')
        closest_sensor = max(range(5), key=prox_sensors.__getitem__)
        if prox_sensors[closest_sensor] > ThymioII.threshold:
            ThymioII.turn_decider[closest_sensor](self)
        
        glib.timeout_add(10, self.check_prox)


def main(name='thymio-II'):

    robot = ThymioII(name)

    robot.check_prox()
    robot.move_forward(500)
    robot.run()
        
if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except IndexError:
        main()
