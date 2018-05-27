

def move_BF(channel):
    
    if CG.state != "Playing":
        print('You have to start a game first')
    else:
        print(channel)
        if CG.get_mode() != "manual":
            print('Somebody is playing remotely at the moment')
        
        else:
            if (GPIO.input(RPi_pins["back"]))^(GPIO.input(RPi_pins["front"])):
                print("back/front")
                if GPIO.input(RPi_pins["back"]):
                    #while not GPIO.input(RPi_pins["endBack"]):
                        CG.AxisBF.move("back")

                else:
                    #while not GPIO.input(RPi_pins["endFront"]):
                        CG.AxisBF.move("front")
            else:
                if GPIO.input(RPi_pins["back"]) and GPIO.input(RPi_pins["front"]):
                    raise ValueError('Invalid Controller Value!')
                CG.AxisBF.move("none")


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
                if GPIO.input(RPi_pins["left"]) and GPIO.input(RPi_pins["right"]):
                    raise ValueError('Invalid Controller Value!')
                CG.AxisLR.move("none")


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
                    print("up")

            else:
                if GPIO.input(RPi_pins["down"]) and GPIO.input(RPi_pins["up"]):
                    raise ValueError("Invalid Controller Value!")
    
                CG.AxisDU.move("none")