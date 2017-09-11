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
    
    def __init__(self, name):
        Aseba.__init__(self)

        nodes = self.network.GetNodesList()
        if name not in nodes:
            nodes = map(str, list(nodes))
            raise AsebaException("Cannot find node {nodeName}! "
                                 "These are the available nodes: {nodes}" \
                                 .format(nodeName=name, nodes=list(nodes)))
        self.name = name
        self.load_scripts(path.realpath('./example.aesl'))

    def __enter__():
        pass

    def move_forward(self, speed):
        self.network.SetVariable(self.name, 'motor.left.target', [speed])
        self.network.SetVariable(self.name, 'motor.right.target', [speed])

    def stop(self):
        self.move_forward(0)

    def _turn(self, direction, deg):
        radians = math.pi * deg / 180
        speed = self.network.GetVariable(self.name,
                'motor.{dir}.speed'.format(dir=direction))

        cms_speed = speed[0] * 20 / 500 * 0.75
        time_stop = ThymioII.wheel_distance * radians / cms_speed
        self.network.SetVariable(self.name,
                'motor.{dir}.target'.format(dir=direction),
                [0])
        time.sleep(time_stop)
        self.network.SetVariable(self.name,
                'motor.{dir}.target'.format(dir=direction),
                [speed[0]])

    def turn_left(self, deg):
        self._turn('left', deg)

    def turn_right(self, deg):
        self._turn('right', deg)

def main(name='thymio-II'):

    robot = ThymioII(name)

    def on_prox(prox_sensors):
        if any(prox_sensor > 500 for prox_sensor in prox_sensors):
            robot.stop()
            robot.close()

    robot.on_event('Prox', on_prox)
    robot.move_forward(100)
    robot.run()
        
if __name__ == '__main__':
    main(sys.argv[1])
