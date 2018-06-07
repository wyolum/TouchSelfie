'''
    Basic interface for hardware buttons
    Laurent Alacoque 2o18
'''

RPI_GPIO_EXISTS = True

# Predefine variables
BUTTONS_PINS = []
BUTTONS_MODE = 0
BUTTON_IS_ACTIVE = 1

try:
    import RPi.GPIO as GPIO
    ## GPIO pin definition for hardware buttons
    BUTTONS_PINS = [10,8,12]
    BUTTONS_MODE = GPIO.PUD_DOWN # switch to VDD, configure io in pulldown
    BUTTON_IS_ACTIVE = 1         # active 1 GPIO (pull_down with switch to VDD)
except ImportError:
    RPI_GPIO_EXISTS = False



class Buttons():
    def __init__(self, buttons_pins=BUTTONS_PINS, mode=BUTTONS_MODE, active_state=BUTTON_IS_ACTIVE):
        self.buttons_pins = buttons_pins
        self.mode = mode
        self.active_state = active_state
        if RPI_GPIO_EXISTS:
            GPIO.setmode(GPIO.BOARD)
            for pin in self.buttons_pins:
                GPIO.setup(pin, GPIO.IN, pull_up_down = self.mode)
            if len(buttons_pins) != 0:
                self._has_buttons = True
            else:
                self._has_buttons = False
        else:
            self._has_buttons = False
    
    def __del__(self):
        if self._has_buttons:
            GPIO.cleanup()
            
    def has_buttons(self):
        return self._has_buttons
        
    def buttons_number(self):
        return len(self.buttons_pins)
        
    def state(self):
        if not self._has_buttons:
            return 0
        
        for i,pin in enumerate(self.buttons_pins,1):
            if GPIO.input(pin) == self.active_state:
                return i
        else :
            # reached the end of pins, none active
            return 0
        
if __name__ == '__main__':
    import time
    import sys
    buttons = Buttons()
    last = 0
    if buttons.has_buttons():
        print "Press hardware buttons to see change, ctrl+C to exit"
    else:
        print "No button configured (no access to GPIO or empty button list)"
        print "Number of buttons is %d" % buttons.buttons_number()
        sys.exit()
        
    while True:
        state = buttons.state()
        if last != state:
            print "new state: %d"%state
            last = state
        time.sleep(0.1)
