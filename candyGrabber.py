import time
import atexit
from axis import MockSwitch, RealSwitch, Motor, Axis


#import RPi.GPIO as GPIO

#from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
#from abc import ABC, abstractmethod

## create a default object, no changes to I2C address or frequency
##mh = Adafruit_MotorHAT(addr=0x60)
#### recommended for auto-disabling motors on shutdown!
##def turnOffMotors():
##    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
##    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
##    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
##    #mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
##atexit.register(turnOffMotors)
#create motors
##m1 = mh.getMotor(1)
##m2 = mh.getMotor(2)
##m3 = mh.getMotor(3)
### set the speed to start, from 0 (off) to 255 (max speed)
##m1.setSpeed(80)
##m2.setSpeed(80)
##m3.setSpeed(80)

#GPIO.setmode(GPIO.BCM)
##Controller pins
#GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
##other pins
#GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #end not reached
#GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # got Candy
#GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Coin inserted

class CandyGrabber:
    # Raspberry Pi pins as a list
    RPi_pins = {"left":24,
            "right":25,
            "front":22,
            "back":23,
            "up":6,
            "down":5,
            "endLeft":18,
            "endRight":17,
            "endFront":13,
            "endBack":12,
            "gotCandy":27,
            "coinInserted":16
    }

    #create endswitches
    EndUD = MockSwitch()
    EndFB = RealSwitch(RPi_pins["endFront"],RPi_pins["endBack"])
    EndLR = RealSwitch(RPi_pins["endLeft"],RPi_pins["endRight"])

    m1="m1"
    m2="m2"
    m3="m3"
    MotorUD = Motor(m3)
    MotorFB = Motor(m1)
    MotorLR = Motor(m2)

    #create axis
    AxisUD = Axis(m3,("up","down"),EndUD)
    AxisFB = Axis(m2,("front","back"),EndFB)
    AxisLR = Axis(m1,("left","right"),EndLR)










