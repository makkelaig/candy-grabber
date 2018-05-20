########Class Axis##############
#                              #
#  Each Axis consists of one   #
#  motor and two endswitches   #
#                              #
################################
import time
import atexit
import RPi.GPIO as GPIO
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from abc import ABC, abstractmethod

#GPIO.setmode(GPIO.BCM)


#abstract base class endswitch
class Endswitch(ABC):
    
    def __init__(self):
        super().__init__()

    def get_endCW(self):
        pass
    #return self._endCW
    def get_endCCW(self):
        pass
#return self._endCCW


#child class for real endswitch
class RealSwitch(Endswitch):
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


#child class for mock endswitch
class MockSwitch(Endswitch):
    _end_cw = False
    _end_ccw = False
    
    #takes no arguments
    def __init__(self):
        self._counter = 0
    
    def get_end_cw(self):
        if (self._counter >= 3):
            self._end_cw = True
        else:
            self._end_cw = False
        return self._end_cw
    
    def get_end_ccw(self):
        if (self._counter <= 0):
            self._end_ccw = True
            self.reset_counter()
        else:
            self._end_ccw = False
        return self._end_ccw
    
    def increase_counter(self):
        self._counter += 1
    
    def decrease_counter(self):
        self._counter -= 1
    
    def reset_counter(self):
        self._counter = 0
    
    def print_counter(self):
        print(self._counter)


class Motor:
    #takes the mh.motor as input
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
    # parameters are: motor-object, directions, endswitch object
    # directions is a tuple with two strings, i.e. ("right","left")
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
                if (self.endswitch.__class__.__name__ == "MockSwitch"):
                    self.endswitch.increase_counter()
                    self.endswitch.print_counter()
            
            else:
                print("End reached", direction)
                if (self.endswitch.__class__.__name__ == "MockSwitch"):
                    self.endswitch.decrease_counter()
        
        else:
            if not self.endswitch.get_end_ccw():
                self.motor.move_ccw()
                if (self.endswitch.__class__.__name__ == "MockSwitch"):
                    self.endswitch.decrease_counter()
                    self.endswitch.print_counter()           
            else:
                print("End reached", direction)

#usage example
#m2 = "m2"
#EndUpDown = MockSwitch()
#Motor2 = Motor(m2)
#Axis2 = Axis(Motor2,("up","down"),EndUpDown)
#print(EndUpDown.__class__.__name__)
#if (Axis2.endswitch.__class__.__name__ == "MockSwitch"):
#    print("class name is MockSwitch")
#
#Axis2.move("up")
#Axis2.move("up")
#Axis2.move("none")
#Axis2.move("down")



