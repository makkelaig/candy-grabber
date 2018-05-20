import random
from axis import MockSwitch, RealSwitch, Motor, Axis
from transitions import Machine



class CandyGrabber:
    
    states = ['Stopped', 'Idle', 'Playing', 'Complete']
    transitions = [
                   { 'trigger': 'reset', 'source': ['Complete','Stopped'], 'dest': 'Idle','before':'reset_game','after':'game_ready' },
                   { 'trigger': 'start', 'source': 'Idle', 'dest': 'Playing', 'before':'set_mode' },
                   { 'trigger': 'stop', 'source': '*', 'dest': 'Stopped', 'before':'stop_game' },
                   { 'trigger': 'finish', 'source': 'Playing', 'dest': 'Complete' }
                   ]

    def __init__(self):
        self.machine = Machine(model=self, states=CandyGrabber.states, transitions=CandyGrabber.transitions, initial='Stopped')
        #mode can be 'none', 'remote' or 'manual'
        self.mode = 'none'
    

    def set_mode(self,mode_in):
        
        if self.mode == 'none':
            ret = True
            self.mode = mode_in
            print('mode is:', self.mode)
        
        else:
            print('Sorry, somebody is playing at the moment')
            ret = False
                
        return ret

    def game_ready(self):
        print('Ready, waiting for player')

    def reset_game(self):
        print('resetting')
        self.mode = 'none'


    def stop_game(self):
        #turn off motors
        print('stopping')


CG = CandyGrabber()
CG.state
