#!/usr/bin/python

import dbus
import dbus.mainloop.glib
import glib
import gobject
import os
import sys


class ThymioController(object):
    def __init__(self, filename):
        # init the main loop and joystick
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        
        # get stub of the Aseba network
        bus = dbus.SessionBus()
        asebaNetworkObject = bus.get_object('ch.epfl.mobots.Aseba', '/')
        self.asebaNetwork = dbus.Interface(asebaNetworkObject,
            dbus_interface='ch.epfl.mobots.AsebaNetwork')
        
        # load the file
        self.asebaNetwork.LoadScripts(
            os.path.realpath(sys.argv[1]),
            reply_handler=self.dbusReply,
            error_handler=self.dbusError
        )
        
        # schedules first scan of joystick
        glib.timeout_add(20, self.scanJoystick)
    
    def run(self):
        # run event loop
        self.loop = gobject.MainLoop()
        self.loop.run()
    
    def dbusReply(self):
        # correct replay on D-Bus, ignore
        pass

    def dbusError(self, e):
        # there was an error on D-Bus, stop loop
        print('dbus error: %s' % str(e))
        self.loop.quit()

    def scanJoystick(self):
        self.asebaNetwork.SendEventName('SetSpeed',
            [0, 0],
            reply_handler=self.dbusReply,
            error_handler=self.dbusError
        )

        self.asebaNetwork.SendEventName('SetSpeed',
            [0, 0],
            reply_handler=self.dbusReply,
            error_handler=self.dbusError
        )
        
        # send color command
        # if cmp(c, self.oc) != 0:
            # self.asebaNetwork.SendEventName('SetColor',
                # map(lambda x: 32*x, c),
                # reply_handler=self.dbusReply,
                # error_handler=self.dbusError
            # )
            # self.oc = c
        
        # read and display horizontal sensors
        horizontalProximity = self.asebaNetwork.GetVariable(
            'thymio-II', 'prox.horizontal')
        print(', '.join(map(str, horizontalProximity)))
        
        # reschedule scan of joystick
        glib.timeout_add(20, self.scanJoystick)


def main():
    # check command-line arguments
    if len(sys.argv) != 2:
        print('Usage %s FILE' % sys.argv[0])
        return
    
    # create and run controller
    thymioController = ThymioController(sys.argv[1])
    thymioController.run()


if __name__ == '__main__':
    main()
