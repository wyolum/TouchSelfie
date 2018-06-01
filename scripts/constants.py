EFFECTS = ["None", "Warhol", "Four"]

SCREEN_W = 800 ## raspi touch
SCREEN_H = 480 ## raspi touch

#Raspicam v2 stills dimensions
CAM_W = 3280
CAM_H = 2464

#Desired snapshot size
SNAP_W = 1640
SNAP_H = 1232
#Desired size of the embedded logo
LOGO_MAX_SIZE = 256
LOGO_PADDING = 64

# Snapshot to screen scale
# Based on width
SNAP_TO_SCREEN_SCALE = max([1.0 * SNAP_W / SCREEN_W, 1.0 * SNAP_H / SCREEN_H])

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


## GPIO pin definition for hardware buttons
BUTTON1_PIN = 10
BUTTON2_PIN = 8
BUTTON3_PIN = 12
BUTTON_IS_ACTIVE = 1 # active 1 GPIO (pull_down with switch to VDD)

## GIF parameters
GIF_SIZE = (800, 800)
GIF_FRAMES_NUMBER = 10
GIF_ACQ_INTERFRAME_DELAY_MILLIS = 400
GIF_INTERFRAME_DELAY_MILLIS     = 100
GIF_OUT_FILENAME = "animation.gif"

## Collage embellishment
COLLAGE_FRONT_ENVELOPPE = "collage_four_square.png"
