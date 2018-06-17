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

""" GPIO Setup """
GPIO.setmode(GPIO.BCM)
# Controller pins
GPIO.setup(RPi_pins["back"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RPi_pins["front"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RPi_pins["left"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RPi_pins["right"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RPi_pins["up"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RPi_pins["down"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# other pins
GPIO.setup(RPi_pins["endRight"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RPi_pins["endLeft"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RPi_pins["endBack"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RPi_pins["endFront"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RPi_pins["gotCandy"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RPi_pins["coinInserted"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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


""" //////////////////// methods /////////////////////// """


def move_claw(direction):
    
    """
    method move_claw for subhandler_direction in opcua server
    """
    
    print("move method call with parameter: ", direction)
    
    if CG.state != "Playing":
        #message.set_value("You have to start a game first")
        ret = False
    else:
        if CG.get_mode() != "remote":
            print("Somebody is playing manually at the moment")
            message.set_value("Somebody is playing manually at the moment")
            ret = False
        else:
            if direction == "none":
                CG.stop_claw()
            elif direction in ["left","right"]:
                CG.AxisLR.move(direction)
            elif direction in ["down","up"]:
                CG.AxisDU.move(direction)
            else:
                CG.AxisBF.move(direction)
            ret = True
            return ret


""" //////////// subhandler classes for opcua server ////////// """

class SubHandler_mode(object):
    
    """
    Subscription Handler: reacts to mode changes and updates mode of CG object
    """
    
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        CG.set_mode(val)
    
    def event_notification(self, event):
        print("Python: New event", event)



class SubHandler_direction(object):
    
    """
    Subscription Handler: moves claw when a direction button is pressed in user interface;
    direction val can be "left", "right", "front", "back", "up", "down" or "none"
    """
 
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        move_claw(val)
    
    def event_notification(self, event):
        print("Python: New event", event)



class SubHandler_start(object):
    
    """
    Subscription Handler: reacts to dashboard buttons "Start" (start=True) and "Stop" (start=False)
    """
    
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        if val==True:
            if CG.state == "Stopped":
                CG.reset()          
                CG.start("remote")
            else:
                CG.start("remote")
            message.set_value("ready to play!")
                
        else:
            if CG.mode == "remote":
                CG.stop()
                CG.reset()
                state.set_value(CG.state)
                mode.set_value(CG.mode)
                print("stopping game:", state.get_value(), mode.get_value())
                message.set_value("Stopped game, press start if you want to go again")
            
        state.set_value(CG.state)


class SubHandler_timer(object):
    
    """
    Subscription Handler: stops game if timer variable is set, resets timer
    """
    
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        if val == 1:
            CG.quit_game(0) # lost game
            state.set_value(CG.state)
            start.set_value(0)
            timer.set_value(0)
            message.set_value("Sorry, time's up. You Lost!")   


""" ///////////// callback functions for manual mode ////////////// """

""" 
methods for physical controller switches
"""

# move back/none/front
def move_BF(channel):
    if CG.state != "Playing":
        print("You have to start a game first")
    else:
        print(channel)
        if CG.get_mode() != "manual":
            print("Somebody is playing remotely at the moment")
        else:
            if (GPIO.input(RPi_pins["back"]))^(GPIO.input(RPi_pins["front"])):
                if GPIO.input(RPi_pins["back"]):
                    CG.AxisBF.move("back")
                else:
                    CG.AxisBF.move("front")
            else:
                CG.AxisBF.move("none")
                if GPIO.input(RPi_pins["back"]) and GPIO.input(RPi_pins["front"]):
                    raise ValueError("Invalid Controller Value!")

# move left/none/right
def move_LR(channel):
    if CG.state != "Playing":
        print("You have to start a game first")
    else:
        print(channel)
        if CG.get_mode() != "manual":
            print("Somebody is playing remotely at the moment")
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
                    raise ValueError("Invalid Controller Value!")

# move down/none/up
def move_DU(channel):
    if CG.state != "Playing":
        print("You have to start a game first")
    else:
        print(channel)
        if CG.get_mode() != "manual":
            print("Somebody is playing remotely at the moment")
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
    """
    start game if coin inserted
    """
    if CG.mode == "none":
        if CG.state == "Stopped":
            CG.reset()
        CG.start("manual")

def won_game(channel):
    """
    quit game when got candy
    """
    if GPIO.input(RPi_pins["gotCandy"])==1:
        #print(GPIO.input(RPi_pins["gotCandy"]))
        if CG.mode == "remote":
            message.set_value("You Won!")
        CG.quit_game(True) #won game
        state.set_value(CG.state)
        start.set_value(0)
    
# add gpio events and define callbacks
GPIO.add_event_detect(RPi_pins["back"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["front"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["left"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["right"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["down"], GPIO.BOTH, callback= move_DU)
GPIO.add_event_detect(RPi_pins["up"], GPIO.BOTH, callback= move_DU)
GPIO.add_event_detect(RPi_pins["coinInserted"], GPIO.RISING, callback= start_manual)
GPIO.add_event_detect(RPi_pins["gotCandy"], GPIO.RISING, callback = won_game)


""" //////////////////////////// main /////////////////////////////////// """

if __name__ == "__main__":
    
    # optional: setup logging
    logging.basicConfig(level=logging.WARN)
    
    # setup server
    server = Server()
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    server.set_server_name("FreeOpcUa Example Server")
    
    # setup our own namespace
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)
    
    # get objects node, this is where we should put our nodes
    objects = server.get_objects_node()
    
    # create a new node type we can instantiate in our address space
    candyGrabber = objects.add_object(idx, "CandyGrabber")
    # with features
    state = candyGrabber.add_variable(idx, "State", "Stopped")
    start = candyGrabber.add_variable(idx,"Start", 0)
    start.set_writable()
    direction = candyGrabber.add_variable(idx, "Direction", "none")
    direction.set_writable()
    mode = candyGrabber.add_variable(idx, "Mode", "none")
    mode.set_writable()
    message = candyGrabber.add_variable(idx, "Message", "Hi there, press start if you want to play")
    message.set_writable()
    timer = candyGrabber.add_variable(idx, "Timer", 0)
    timer.set_writable()
    
    # starting!
    server.start()
    print("Available loggers are: ", logging.Logger.manager.loggerDict.keys())
    
    try:

        # create handler objects
        mode_handler = SubHandler_mode()
        direction_handler = SubHandler_direction()
        start_handler = SubHandler_start()
        timer_handler = SubHandler_timer()
        
        # subscribe to nodes on server side
        sub_dir = server.create_subscription(100, handler=direction_handler)
        sub_mode = server.create_subscription(50, mode_handler)
        sub_start = server.create_subscription(50, start_handler)
        sub_timer = server.create_subscription(30, timer_handler)
        
        handle_mode = sub_mode.subscribe_data_change(mode)
        handle_dir = sub_dir.subscribe_data_change(direction)
        handle_start = sub_start.subscribe_data_change(start)
        handle_timer = sub_timer.subscribe_data_change(timer)
        
        # embed interactive shell
        embed()
        
        # reset Candy Grabber
        CG.reset()
        print(mode)
        message.set_value("Hello, press start to play!")
        print(message)
        
    finally:
        server.stop()           # stop server
        GPIO.cleanup()          # clean up GPIO settings
        CG.stop_claw()          # stop motors
        print("cleaned up")







