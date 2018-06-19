
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
    "pull_up_down": 1,        # GPIO.PUD_DOWN=1 GPIO_PUD_UP = 2 => switch to VDD, configure io in pulldown
    "active_state": 1         # active 1 GPIO (pull_down with switch to VDD)
}


EMAIL_BUTTON_IMG  = "ressources/ic_email.png"
OAUTH2_REFRESH_PERIOD = 1800000 # interval between two OAuth2 token refresh (ms)
HARDWARE_POLL_PERIOD = 100      # poll interval for buttons (ms)




# Some customizations
from PIL import Image
import os
class Config():

# Adapt this to your own needs
    logo        = Image.open("logo.png") # Logo for the "None" effect
    countdown1  = 5 # seconds of preview before first snap
    countdown2  = 3 # seconds of preview between snaps (Four pictures mode)
    photoCaption = "Photo from xxx Event" # Caption in the photo album
    ARCHIVE      = True # Do we archive photos locally
    archive_dir  = os.path.join("..","Photos") # Where do we archive photos
    albumID      = None # Will be overwritten with the album id string contained in "album.id" => use install_credentials.py to create 'album.id'
    emailSubject = "Here's your photo!" # subject line of the email sent from the photobooth
    emailMsg     = "Greetings, here's your photo sent from the photobooth" # Brief body of the message sent from the photobooth

# No need to change below
    def __init__(self):
        try:
            handle = open("album.id","r")
            self.albumID = handle.readline().strip()
            handle.close()
            if self.albumID == "" or self.albumID == None:
                print "Wrong 'album.id' file, run 'install_credentials.py to select album"
                self.albumID = None
        except:
            print "Error while reading 'album.id', run 'install_credentials.py' to select album"

custom = Config()
    
