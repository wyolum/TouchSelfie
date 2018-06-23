
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
    "pull_up_down": "pull_down",        # pull_up or pull_down
    "active_state": 1         # active 1 GPIO (pull_down with switch to VDD)
}


EMAIL_BUTTON_IMG  = "ressources/ic_email.png"
OAUTH2_REFRESH_PERIOD = 1800000 # interval between two OAuth2 token refresh (ms)
HARDWARE_POLL_PERIOD = 100      # poll interval for buttons (ms)

CONFIGURATION_FILE = "configuration.json"
APP_ID_FILE = "client_id.json"
CREDENTIALS_STORE_FILE = "credentials.dat"
