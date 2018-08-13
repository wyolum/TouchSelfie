"""
Constants for the TouchSelfie program

.. py:data:: SCREEN_H,SCREEN_W
    Dimensions in pixels of the screen attached (will be used to compute layout)
.. py:data:: EFFECT_PARAMETERS
    A dict of dict data structure to tune acquisition parameters for each snap effct
.. py:data:: SOFTWARE_BUTTONS
    A dict of dict data structure to tune software buttons (in case of no hardware buttons)
.. py:data:: HARDWARE_BUTTONS
    configuration of the hardware buttons' GPIO pins, pull_up_down state and active state
.. py:data:: EMAIL_BUTTON_IMG  
    'send_email' button icon
.. py:data:: OAUTH2_REFRESH_PERIOD
    interval between two OAuth2 token refresh (ms)
.. py:data:: HARDWARE_POLL_PERIOD = 100
    polling interval to detect hardware buttons change (ms)

.. py:data:: CONFIGURATION_FILE
    name of the configuration file (relative to scripts/ directory)
.. py:data:: APP_ID_FILE
    name of the 'application_secret' file downloaded from console.developers.google.com (relative to scripts/ directory)
.. py:data:: CREDENTIALS_STORE_FILE
    name of the automaticaly generated credentials store (relative to scripts/ directory)

"""
import os
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
        "icon" : os.path.join("ressources","ic_photo.png")
        },
    "Four": {
        "icon" : os.path.join("ressources","ic_portrait.png")
        },
    "Animation": {
        "icon" : os.path.join("ressources","ic_anim.png")
        }
}

HARDWARE_BUTTONS = {
    "button_pins": [10,8,12], # Change this and the following to reflect your hardware buttons
    "pull_up_down": "pull_down",        # pull_up or pull_down
    "active_state": 1         # active 1 GPIO (pull_down with switch to VDD)
}

ACTIONS_KEYS_MAPPING = {
    "snap_None": ["s","S","<F1>"],
    "snap_Four": ["f","F","<F2>"],
    "snap_Animation": ["a","A","<F3>"],
    "send_email":["e","@"],
    "configure":["<Escape>"]
    #,"send_print":["P"] #Uncomment if you want to a keyboard shortcut for printing
}

COUNTDOWN_OVERLAY_IMAGES=[
    os.path.join("ressources","count_down_1.png"),
    os.path.join("ressources","count_down_2.png"),
    os.path.join("ressources","count_down_3.png"),
    os.path.join("ressources","count_down_4.png"),
    os.path.join("ressources","count_down_5.png"),
    os.path.join("ressources","count_down_ready.png")]
COUNTDOWN_IMAGE_MAX_HEIGHT_RATIO = 0.2 #(0. - 1.) Ratio of the countdown images over screen height

EMAIL_BUTTON_IMG  = os.path.join("ressources","ic_email.png")
PRINT_BUTTON_IMG  = os.path.join("ressources","ic_print.png")
OAUTH2_REFRESH_PERIOD = 1800000 # interval between two OAuth2 token refresh (ms)
HARDWARE_POLL_PERIOD = 100      # poll interval for buttons (ms)

CONFIGURATION_FILE = "configuration.json"
APP_ID_FILE = "client_id.json"
CREDENTIALS_STORE_FILE = "credentials.dat"
EMAILS_LOG_FILE = os.path.join("..","sendmail.log") # you should activate 'enable_mail_logging' key in configuration.json
