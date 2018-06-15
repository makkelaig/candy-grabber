######## Class Axis ############
#                              #
#  Each Axis consists of one   #
#  motor and two end-switches  #
#                              #
################################

import time
import atexit
import RPi.GPIO as GPIO
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from abc import ABC, abstractmethod


class Endswitch(ABC):
    """
    Abstract base class endswitch
    """
    
    def __init__(self):
        super().__init__()

    def get_end_cw(self):
        pass

    def get_end_ccw(self):
        pass



class RealSwitch(Endswitch):
    """
    Child class for real endswitch
    """
    _end_cw = False
    _end_ccw = False
    
    #takes endswitch pin numbers as arguments
    def __init__(self, pin_end_cw, pin_end_ccw):
        self.pinCW = pin_end_cw
        self.pinCCW = pin_end_ccw
    
    def get_end_cw(self):
        self._end_cw = GPIO.input(self.pinCW)
        return self._end_cw
    
    def get_end_ccw(self):
        self._end_ccw = GPIO.input(self.pinCCW)
        return self._end_ccw


class MockSwitch(Endswitch):
    """
    Child class for mock endswitch
    """
    _end_cw = False
    _end_ccw = False
    
    #takes no arguments
    def __init__(self):
        self._counter = 0
    
    def get_end_cw(self):
        return False

    def get_end_ccw(self):
        return False


class Motor:
    """
    takes the mh.motor object as input
    """
    def __init__(self,motorId):
        self.Id = motorId
    
    def move_cw(self):
        print("move cw motor",self.Id)
        self.Id.run(Adafruit_MotorHAT.FORWARD)
        time.sleep(0.1)
    
    def move_ccw(self):
        print("move ccw motor ", self.Id)
        self.Id.run(Adafruit_MotorHAT.BACKWARD)
        time.sleep(0.1)
    
    def stop(self):
        print("stop motor " ,self.Id)
        self.Id.run(Adafruit_MotorHAT.RELEASE)
        time.sleep(0.1)


class Axis:
    """
    An Axis consists of a motor and an endswitch
    parameters are: Motor-object, directions, Endswitch object;
    directions is a tuple with two strings, i.e. ("right","left")
    """
    def __init__(self,motor,directions_array,Endswitch):
        self.motor = motor
        self.endswitch = Endswitch
        self.directions = directions_array
    
    def move(self,direction):
        
        if direction == "none":
            self.motor.stop()
        
        elif self.directions[0] == direction:
            if not self.endswitch.get_end_cw():
                self.motor.move_cw()

            if self.endswitch.get_end_cw():
                print('End reached', direction)
                self.motor.stop()

        else:
            if not self.endswitch.get_end_ccw():
                self.motor.move_ccw()
        
            if self.endswitch.get_end_ccw():
                print('End reached', direction)
                self.motor.stop()

#usage example
#m2 = "m2"
#EndUpDown = MockSwitch()
#Motor2 = Motor(m2)
#Axis2 = Axis(Motor2,("up","down"),EndUpDown)
#print(EndUpDown.__class__.__name__)
#if (Axis2.endswitch.__class__.__name__ == "MockSwitch"):
#print("class name is MockSwitch")
#Axis2.move("up")
#Axis2.move("up")
#Axis2.move("none")
#Axis2.move("down")



