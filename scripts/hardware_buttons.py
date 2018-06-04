'''
    Basic interface for hardware buttons
    Laurent Alacoque 2o18
'''

import RPi.GPIO as GPIO

## GPIO pin definition for hardware buttons
BUTTONS_PINS = [10,8,12]
BUTTONS_MODE = GPIO.PUD_DOWN # switch to VDD, configure io in pulldown
BUTTON_IS_ACTIVE = 1         # active 1 GPIO (pull_down with switch to VDD)


class Buttons():
    def __init__(self, buttons_pins=BUTTONS_PINS, mode=BUTTONS_MODE, active_state=BUTTON_IS_ACTIVE):
        self.buttons_pins = buttons_pins
        self.mode = mode
        self.active_state = active_state
        GPIO.setmode(GPIO.BOARD)
        for pin in self.buttons:
            GPIO.setup(pin, GPIO.IN, pull_up_down = self.mode)
    def __del__(self):
        GPIO.cleanup()
    def buttons_state(self):
        ret = 0 # no button pressed
        for i,pin in enumerate(self.buttons_pins,1):
            if GPIO.input(pin) == self.active_state:
                return i
        else :
            # reached the end of pins, none active
            return 0
        
 if __name__ == '__main__':
    import time
    buttons = Buttons()
    last = 0
    while True:
        state = buttons.state():
        if last != state:
            print "new state: %d",state
            last = state
        time.sleep(0.1)
