############################################
#                                          #
#  Candy Grabber class with state machine  #
#                                          #
############################################

import random
from axis import MockSwitch, RealSwitch, Motor, Axis
from transitions import Machine
"""
    State machine by Tal Yarkoni, Alexander Neumann and others, 
    available at: https://github.com/pytransitions/transitions.git
"""

class CandyGrabber:
    """
    abstract representation of a toy candy grabber, 
    """
    
    coin_inserted = False
    
    states = ['Stopped', 'Idle', 'Playing']
    transitions = [
                   { 'trigger': 'reset', 'source':'Stopped', 'dest': 'Idle','before':'reset_game','after':'game_ready' },
                   { 'trigger': 'start', 'source': 'Idle', 'dest': 'Playing', 'before':'set_mode' },
                   { 'trigger': 'stop', 'source': '*', 'dest': 'Stopped', 'before':'stop_claw' },
                   ]

    def __init__(self, AxisBF, AxisLR, AxisDU):
        self.machine = Machine(model=self, states=CandyGrabber.states, transitions=CandyGrabber.transitions, initial='Stopped')
        #mode can be 'none', 'remote' or 'manual'
        self.mode = 'none'
        self.AxisBF = AxisBF
        self.AxisLR = AxisLR
        self.AxisDU = AxisDU

    def set_mode(self,mode_in):
        
        if self.mode == 'none':
            ret = True
            self.mode = mode_in
            print('mode is:', self.mode)
        
        else:
            print('Sorry, somebody is playing at the moment')
            ret = False
                
        return ret
    
    def get_mode(self):
        print(self.mode)
        return self.mode

    def game_ready(self):
        print('Ready, waiting for player')

    def reset_game(self):
        print('resetting')
        self.mode = 'none'

    def stop_claw(self):
        #turn off motors
        self.AxisLR.move('none')
        self.AxisBF.move('none')
        self.AxisDU.move('none')
        print('stopping motors')

    def quit_game(self,won):
        if self.state == 'Playing':
            if won==True:
                print('Congratulations! You Won! get your candy')
            else:
                print('sorry, the time is up. You Lost!')
            self.stop()
            self.reset()

