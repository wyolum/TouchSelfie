
SCREEN_W = 800 ## raspi touch
SCREEN_H = 480 ## raspi touch

EFFECTS_PARAMETERS = {
    "None": {
        'snap_size' : (1640,1232),
        'logo_size' : 128,
        'logo_padding' : 32
    },
    "Four": { 
        'snap_size' : (820,616),
        'foreground_image' : "collage_four_square.png"
    },
    "Animation": {
        'snap_size' : (500, 500),
        'frame_number' : 10,
        'snap_period_millis' : 200,
        'gif_period_millis' : 50
    }
}

SOFTWARE_BUTTONS = {
    "None": {
        "icon" : "ressources/ic_photo.png"
        },
    "Four": {
        "icon" : "ressources/ic_portrait.png"
        },
    "Animation": {
        "icon" : "ressources/ic_anim.png"
        }
}

HARDWARE_BUTTONS = {
    "button_pins": [10,8,12], # Change this and the following to reflect your hardware buttons
    "pull_up_down": 1, #GPIO.PUD_DOWN=1 GPIO_PUD_UP = 2 => switch to VDD, configure io in pulldown
    "active_state": 1         # active 1 GPIO (pull_down with switch to VDD)
}

CONFIG_BUTTON_IMG = "ressources/ic_settings.png"
EMAIL_BUTTON_IMG  = "ressources/ic_email.png"

HARDWARE_POLL_PERIOD = 100 #poll interval for buttons (ms)