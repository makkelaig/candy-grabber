import time
import atexit
import RPi.GPIO as GPIO
from axis import MockSwitch, RealSwitch, Motor, Axis
#from controller import Controller
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
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


##class Candygrabber:
##    _states = ("Stopped","Idle","Execute","Won", "Lost")
##    _commands = ()

#create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)
#create motors
m1 = mh.getMotor(1)
m2 = mh.getMotor(2)
m3 = mh.getMotor(3)
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


def move_BF(channel):     
    print(channel)
    if (GPIO.input(RPi_pins["back"]))^(GPIO.input(RPi_pins["front"])):
        print("back/front")
        if GPIO.input(RPi_pins["back"]):
            if not GPIO.input(RPi_pins["endBack"]):
                AxisBF.move("back")
            else:
                print("End Reached back")
                AxisBF.move("none")
        if GPIO.input(RPi_pins["front"]):   
            if not GPIO.input(RPi_pins["endFront"]):
                AxisBF.move("front")
            else:
                print("End Reached front")
                AxisBF.move("none")
    else:
        if GPIO.input(RPi_pins["back"]) and GPIO.input(RPi_pins["front"]):
            AxisBF.move("none")
            time.sleep(3)
            raise ValueError("Invalid Controller Value!")
            
        AxisBF.move("none")
        time.sleep(0.1)
    
def move_LR(channel):
    print(channel)
    if (GPIO.input(RPi_pins["left"]))^(GPIO.input(RPi_pins["right"])):
        print("left/right")
        if GPIO.input(RPi_pins["left"]):
            if not GPIO.input(RPi_pins["endLeft"]):
                AxisLR.move("left")
            else:
                print("End Reached Left")
                AxisLR.move("none")
                #time.sleep(0.1)
        if GPIO.input(RPi_pins["right"]):   
            if not GPIO.input(RPi_pins["endRight"]):
                AxisLR.move("right")
            else:
                print("End Reached Right")
                AxisLR.move("none")
    else:
        if GPIO.input(RPi_pins["left"]) and GPIO.input(RPi_pins["right"]):
            AxisLR.move("none")
            time.sleep(3)
            raise ValueError("Invalid Controller Value!")
            
        AxisLR.move("none")
        time.sleep(0.1)

def move_DU(channel):
    print(channel)
    if (GPIO.input(RPi_pins["down"]))^(GPIO.input(RPi_pins["up"])):
        print("down/up")
        if GPIO.input(RPi_pins["down"]):
            #if not AxisDU.endSwitch.get_end_cw():
                AxisDU.move("down")
            #else:
             #   print("End Reached bottom")
              #  AxisDU.move("none")
                #time.sleep(0.1)
        if GPIO.input(RPi_pins["up"]):   
            #if not AxisDU.endSwitch.get_end_ccw():
                AxisDU.move("up")
            #else:
               # print("End Reached top")
                #AxisDU.move("none")
    else:
        if GPIO.input(RPi_pins["down"]) and GPIO.input(RPi_pins["up"]):
            AxisDU.move("none")
            time.sleep(3)
            raise ValueError("Invalid Controller Value!")
            
        AxisDU.move("none")
        time.sleep(0.1)

GPIO.add_event_detect(RPi_pins["back"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["front"], GPIO.BOTH, callback= move_BF)
GPIO.add_event_detect(RPi_pins["left"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["right"], GPIO.BOTH, callback= move_LR)
GPIO.add_event_detect(RPi_pins["down"], GPIO.BOTH, callback= move_DU)
GPIO.add_event_detect(RPi_pins["up"], GPIO.BOTH, callback= move_DU)  

while 1:
    
    try:
        embed()
        #AxisFB.move("back")
        #time.sleep(2)
        #AxisFB.move("none")
        time.sleep(60)
        
    finally:
        GPIO.cleanup()         # clean up after yourself
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    





