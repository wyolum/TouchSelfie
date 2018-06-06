EFFECTS = ["None", "Warhol", "Four"]

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

#Desired snapshot size
SNAP_W = 1640
SNAP_H = 1232
#Desired size of the embedded logo
LOGO_MAX_SIZE = 128
LOGO_PADDING = 32


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


## GPIO pin definition for hardware buttons
BUTTON1_PIN = 10
BUTTON2_PIN = 8
BUTTON3_PIN = 12
BUTTON_IS_ACTIVE = 1 # active 1 GPIO (pull_down with switch to VDD)

## GIF parameters
GIF_SIZE = (500, 500)
GIF_FRAMES_NUMBER = 10
GIF_ACQ_INTERFRAME_DELAY_MILLIS = 200
GIF_INTERFRAME_DELAY_MILLIS     = 50
GIF_OUT_FILENAME = "animation.gif"

## Collage embellishment
COLLAGE_FRONT_ENVELOPPE = "collage_four_square.png"

## Countdown
COUNTDOWN_FONT_SIZE = 100
COUNTDOWN_FONT_FAMILY = 'Times'
