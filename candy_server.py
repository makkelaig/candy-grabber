"""
    Program for controlling the candy grabber remotely or manually
    opc ua server holds opc ua object "CandyGrabber" and object "CG" from type CandyGrabber
    
"""

import sys
sys.path.insert(0, "..")
import RPi.GPIO as GPIO
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import logging
import time
import atexit
from datetime import datetime
from axis import MockSwitch, RealSwitch, Motor, Axis
from stateMachine import CandyGrabber
from opcua import ua, uamethod, Server
import os
import random
# from threading import Timer


""" shell for interaction during runtime """
try:
    from IPython import embed
except ImportError:
    import code
    
    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


""" Motor Setup """
# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# get DC motor objects
m1 = mh.getMotor(1)
m2 = mh.getMotor(2)
m3 = mh.getMotor(3)
# motor mocks for running code without motorshield
##m1="mLR"
##m2="mBF"
##m3="mDU"

# set the speed to start, from 0 (off) to 255 (max speed)
m1.setSpeed(80)
m2.setSpeed(80)
m3.setSpeed(80)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

""" GPIO Setup """
GPIO.setmode(GPIO.BCM)
# Controller pins
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# other pins
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Raspberry Pi pins as a dictionary
RPi_pins = {"left":24,
            "right":25,
            "front":23,
            "back":22,
            "up":5,
            "down":6,
            "endLeft":18,
            "endRight":17,
            "endFront":13,
            "endBack":12,
            "gotCandy":27,
            "coinInserted":16
        }

""" create objects of candy grabber """

# create motors
Motor1 = Motor(m1)
Motor2 = Motor(m2)
Motor3 = Motor(m3)

# create endswitches
EndDU = MockSwitch()
EndBF = RealSwitch(RPi_pins["endBack"],RPi_pins["endFront"])
EndLR = RealSwitch(RPi_pins["endLeft"],RPi_pins["endRight"])

# create axis
AxisBF = Axis(Motor2,("back","front"),EndBF)
AxisLR = Axis(Motor1,("left","right"),EndLR)
AxisDU = Axis(Motor3,("down","up"),EndDU)

# create Candy Grabber object
CG = CandyGrabber(AxisBF,AxisLR,AxisDU)

# timeout for game
#timeout = Timer(40.0,CG.quit_game,(False,), None)



""" ////////////////////////////// methods ///////////////////////////////// """

# method move_claw for subhandler_direction in opcua server
def move_claw(direction):

    print("move method call with parameter: ", direction)
    
    if CG.state != "Playing":
        print('You have to start a game first')
        message.set_value('You have to start a game first')
        ret = False
    else:
        if CG.get_mode() != "remote":
            print('Somebody is playing manually at the moment')
            message.set_value('Somebody is playing manually at the moment')
            ret = False
        else:
            ret = True
            if direction == "none":
                CG.stop_claw()
            elif direction in ["left","right"]:
                CG.AxisLR.move(direction)
            elif direction in ["down","up"]:
                CG.AxisDU.move(direction)
            else:
                CG.AxisBF.move(direction)
            return ret


""" ////////////////////////// subhandler classes for opcua server //////////////////////////// """

class SubHandler_mode(object):
    
    """
    Subscription Handler: reacts to mode changes and updates mode of CG object
    """
    
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        #print(val)
        CG.set_mode(val)
        #move_claw(node,val)
    
    def event_notification(self, event):
        print("Python: New event", event)



class SubHandler_direction(object):
    
    """
    Subscription Handler: moves claw when
    """
 
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        move_claw(val)
    
    def event_notification(self, event):
        print("Python: New event", event)
        #move_claw(val)



class SubHandler_start(object):
    
    """
    Subscription Handler: reacts to dashboard buttons "Start" (start=True) and "Stop" (start=False)
    """
    
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        ret = False
        if val==True:
            if CG.state == "Stopped":
                CG.reset()          
                ret = CG.start('remote')
            else:
                ret = CG.start('remote')
                message.set_value("ready to play!")
                
        else:
            if CG.mode == 'remote':
                ret = CG.stop()
                CG.reset()
                state.set_value(CG.state)
                mode.set_value(CG.mode)
                print("stopping game:", state.get_value(), mode.get_value())
                message.set_value("Stopped game, press start if you want to go again")
            else:message.set_value("You have to start a game first")
        return ret



""" //////////////////////////// callback functions for manual mode //////////////////////////// """

""" one method for each controller """

# move back/none/front
def move_BF(channel):
    if CG.state != "Playing":
        print('You have to start a game first')
    else:
        print(channel)
        if CG.get_mode() != "manual":
            print('Somebody is playing remotely at the moment')
        else:
            if (GPIO.input(RPi_pins["back"]))^(GPIO.input(RPi_pins["front"])):
                if GPIO.input(RPi_pins["back"]):
                    CG.AxisBF.move("back")
                else:
                    CG.AxisBF.move("front")
            else:
                CG.AxisBF.move("none")
                if GPIO.input(RPi_pins["back"]) and GPIO.input(RPi_pins["front"]):
                    raise ValueError('Invalid Controller Value!')

# move left/none/right
def move_LR(channel):
    if CG.state != "Playing":
        print('You have to start a game first')
    else:
        print(channel)
        if CG.get_mode() != "manual":
            print('Somebody is playing remotely at the moment')
        else:
            print(channel)
            if (GPIO.input(RPi_pins["left"]))^(GPIO.input(RPi_pins["right"])):
                if GPIO.input(RPi_pins["left"]):
                    CG.AxisLR.move("left")
                else:
                    CG.AxisLR.move("right")
            else:
                CG.AxisLR.move("none")
                if GPIO.input(RPi_pins["left"]) and GPIO.input(RPi_pins["right"]):
                    raise ValueError('Invalid Controller Value!')

# move down/none/up
def move_DU(channel):
    if CG.state != "Playing":
        print('You have to start a game first')
    else:
        print(channel)
        if CG.get_mode() != "manual":
            print('Somebody is playing remotely at the moment')
        else:
            print(channel)
            if (GPIO.input(RPi_pins["down"]))^(GPIO.input(RPi_pins["up"])):
                if GPIO.input(RPi_pins["down"]):
                    CG.AxisDU.move("down")
                
                else:
                    CG.AxisDU.move("up")
            else:
                CG.AxisDU.move("none")
                if GPIO.input(RPi_pins["down"]) and GPIO.input(RPi_pins["up"]):
                    raise ValueError("Invalid Controller Value!")


def start_manual(channel):
    if CG.mode == "none":
        if CG.state == "Stopped":
            CG.reset()
        CG.start("manual")
        timeout.daemon = True
        timeout.start()

def won_game(channel):
    if GPIO.input(RPi_pins["gotCandy"])==1:
        print(GPIO.input(RPi_pins["gotCandy"]))
        CG.quit_game(True)
        timeout.cancel()
        if CG.mode == "remote":
            message.set_value("You Won!")
    
# add gpio events and define callbacks
GPIO.add_event_detect(RPi_pins["back"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["front"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["left"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["right"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["down"], GPIO.BOTH, callback= move_DU)
GPIO.add_event_detect(RPi_pins["up"], GPIO.BOTH, callback= move_DU)
GPIO.add_event_detect(RPi_pins["coinInserted"], GPIO.RISING, callback= start_manual)
GPIO.add_event_detect(RPi_pins["gotCandy"], GPIO.RISING, callback = won_game)
#GPIO.add_event_detect(RPi_pins["endRight"], GPIO.BOTH, callback = end_LR)

if __name__ == "__main__":
    
    # optional: setup logging
    logging.basicConfig(level=logging.WARN)
    
    # setup server
    server = Server()
    #server.disable_clock()
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    server.set_server_name("FreeOpcUa Example Server")
    # setup our own namespace
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)
    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()
    # create a new node type we can instantiate in our address space
    candyGrabber = objects.add_object(idx, "CandyGrabber")
    state = candyGrabber.add_variable(idx, "State", "Stopped")
    start = candyGrabber.add_variable(idx,"Start", 0)
    start.set_writable()        # Set MyVariable to be writable by clients
    #stop = candyGrabber.add_variable(idx,"Stop", 0)
    #stop.set_writable()
    direction = candyGrabber.add_variable(idx, "Direction", "none")
    direction.set_writable()
    mode = candyGrabber.add_variable(idx, "Mode", "none")
    mode.set_writable()
    message = candyGrabber.add_variable(idx, "Message", "Hello")
    mode.set_writable()
    #move_cg = candyGrabber.add_method(idx,"move",move_claw,[ua.VariantType.String])
    
    # starting!
    server.start()
    print("Available loggers are: ", logging.Logger.manager.loggerDict.keys())
    
    try:
        
        # enable following if you want to subscribe to nodes on server side
        mode_handler = SubHandler_mode()
        direction_handler = SubHandler_direction()
        start_handler = SubHandler_start()
        
        sub_dir = server.create_subscription(500, direction_handler)
        sub_mode = server.create_subscription(500, mode_handler)
        sub_start = server.create_subscription(500, start_handler)
        
        handle_mode = sub_mode.subscribe_data_change(mode)
        handle_dir = sub_dir.subscribe_data_change(direction)
        handle_start = sub_start.subscribe_data_change(start)

        embed()
        CG.reset()
        print(mode)
        message.set_value("Hello, press start to play!")
        print(message)
        
    finally:
        #message.set_value("Lost connection to server")
        server.stop()
        GPIO.cleanup()          # clean up GPIO settings
        CG.stop_claw()          # stop motors
        print("cleaned up")







