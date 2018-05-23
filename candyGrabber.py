import sys
sys.path.insert(0, "..")
import logging
import time
import atexit
import RPi.GPIO as GPIO
from datetime import datetime
from axis import MockSwitch, RealSwitch, Motor, Axis
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from stateMachine import CandyGrabber
import time
import os
#import random

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()

from opcua import ua, uamethod, Server

class SubHandler(object):
    
    """
        Subscription Handler. To receive events from server for a subscription
        """
    
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
    
    def event_notification(self, event):
        print("Python: New event", event)

# method to be exposed through server
# uses a decorator to automatically convert to and from variants

#@uamethod
def move_claw(parent, direction):
    print("move method call with parameter: ", direction)
    return True



###create a default object, no changes to I2C address or frequency
##mh = Adafruit_MotorHAT(addr=0x60)
###create motors
##m1 = mh.getMotor(1)
##m2 = mh.getMotor(2)
##m3 = mh.getMotor(3)
### set the speed to start, from 0 (off) to 255 (max speed)
##m1.setSpeed(80)
##m2.setSpeed(80)
##m3.setSpeed(80)
### recommended for auto-disabling motors on shutdown!
##def turnOffMotors():
##    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
##    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
##    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
##
##atexit.register(turnOffMotors)

GPIO.setmode(GPIO.BCM)
#Controller pins
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#other pins
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Raspberry Pi pins as a list
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
m1="mLR"
m2="mBF"
m3="mDU"
Motor1 = Motor(m1)
Motor2 = Motor(m2)
Motor3 = Motor(m3)

#create controllers
#ControllerDU = Controller(("down","up"),(RPi_pins["down"],RPi_pins["up"]))
#ControllerBF = Controller(("back","front"),(RPi_pins["back"],RPi_pins["front"]))
#ControllerLR = Controller(("left","right"),(RPi_pins["left"],RPi_pins["right"]))

#create endswitches
EndDU = MockSwitch()
EndBF = RealSwitch(RPi_pins["endBack"],RPi_pins["endFront"])
EndLR = RealSwitch(RPi_pins["endLeft"],RPi_pins["endRight"])

#create axis
AxisBF = Axis(Motor2,("back","front"),EndBF)
AxisLR = Axis(Motor1,("left","right"),EndLR)
AxisDU = Axis(Motor3,("down","up"),EndDU)

CG = CandyGrabber(AxisBF,AxisLR,AxisDU)

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
                CG
                else:
                    CG.AxisDU.move("up")

            else:
                CG.AxisDU.move("none")
                if GPIO.input(RPi_pins["down"]) and GPIO.input(RPi_pins["up"]):
                    raise ValueError("Invalid Controller Value!")

def end_LR(channel):
    print('Left:', GPIO.input(RPi_pins["endLeft"]))
    print('Right:', GPIO.input(RPi_pins["endRight"]))
    
GPIO.add_event_detect(RPi_pins["back"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["front"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["left"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["right"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["down"], GPIO.BOTH, callback= move_DU)
GPIO.add_event_detect(RPi_pins["up"], GPIO.BOTH, callback= move_DU)
GPIO.add_event_detect(RPi_pins["endLeft"], GPIO.BOTH, callback = end_LR)
GPIO.add_event_detect(RPi_pins["endRight"], GPIO.BOTH, callback = end_LR)

if __name__ == "__main__":
while 1:
    
    try:
        embed()
        #AxisFB.move("back")
        #time.sleep(2)
        #AxisFB.move("none")
        time.sleep(60)
        
    finally:
        server.stop()
        GPIO.cleanup()         # clean up after yourself
##        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
##        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
##        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    





