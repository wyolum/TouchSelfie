from subprocess import call
import tkFileDialog
import glob
import os
import os.path
import time
try:
    import picamera as mycamera
except ImportError:
    import cv2_camera as mycamera
from time import sleep
if False:
    import gdata
    import gdata.photos.service
    import gdata.media
    import gdata.geo
    import gdata.gauth
    import webbrowser
    from datetime import datetime, timedelta
    from oauth2client.client import flow_from_clientsecrets
    from oauth2client.file import Storage
from credentials import OAuth2Login

from PIL import Image
import serial
import config
import custom
import httplib2

from constants import SCREEN_W, SCREEN_H, WHITE, BLACK

FONTSIZE=100
font = ('Times', FONTSIZE)

def safe_set_led(camera, state):
    try:
        camera.led = state
    except:
        pass

def setup_google():
    global client

    out = True
    try:
        # Create a client class which will make HTTP requests with Google Docs server.
        configdir = os.path.expanduser('./')
        client_secrets = os.path.join(configdir, 'OpenSelfie.json')
        credential_store = os.path.join(configdir, 'credentials.dat')

        client = OAuth2Login(client_secrets, credential_store, config.username)

    except KeyboardInterrupt:
        raise
    except Exception, e:
        print 'could not login to Google, check .credential file\n   %s' % e
        out = False
        # raise ### uncomment to debug google oauth shiz
    return out

def countdown(camera, can, countdown1):
    camera.start_preview()
    # camera.start_preview(fullscreen=False,
    #                     crop=(50, 150, 800, 480),
    #                      window=(0, 0, 800, 480),
    #                      hflip=True)
    can.delete("image")
    led_state = False
    safe_set_led(camera, led_state)
    camera.preview_alpha = 100
    camera.preview_window = (0, 0, SCREEN_W, SCREEN_H)
    camera.preview_fullscreen = False

    can.delete("all")

    for i in range(countdown1):
        can.delete("text")
        can.update()
        can.create_text(SCREEN_W/2 - 0, 200, text=str(countdown1 - i), font=font, tags="text")
        can.update()
        if i < countdown1 - 2:
            time.sleep(1)
            led_state = not led_state
            safe_set_led(camera, led_state)
        else:
            for j in range(5):
                time.sleep(.2)
                led_state = not led_state
                safe_set_led(camera, led_state)
    can.delete("text")
    can.update()
    camera.stop_preview()

def setLights(r, g, b):
#    ser = findser()
    rgb_command = 'c%s%s%s' % (chr(r), chr(g), chr(b))
#    ser.write(rgb_command)

def snap(can, countdown1, effect='None'):
    global image_idx

    try:
        if custom.ARCHIVE and os.path.exists(custom.archive_dir) and os.path.exists(custom.PROC_FILENAME):
            ### copy image to archive
            image_idx += 1
            new_filename = os.path.join(custom.archive_dir, '%s_%05d.%s' % (custom.PROC_FILENAME[:-4], image_idx, custom.EXT))
            command = (['cp', custom.PROC_FILENAME, new_filename])
            call(command)
        camera = mycamera.PiCamera()
        countdown(camera, can, countdown1)
        if effect == 'None':
            camera.capture(custom.RAW_FILENAME, resize=(1366, 768))
            snapshot = Image.open(custom.RAW_FILENAME)
        elif effect == 'Warhol': 
            #  set light to R, take photo, G, take photo, B, take photo, Y, take photo
            # merge results into one image
            setLights(255, 0, 0) ## RED
            camera.capture(custom.RAW_FILENAME[:-4] + '_1.' + custom.EXT, resize=(683, 384))
            setLights(0, 255, 0) ## GREEN
            camera.capture(custom.RAW_FILENAME[:-4] + '_2.' + custom.EXT, resize=(683, 384))
            setLights(0, 0, 255) ## BLUE
            camera.capture(custom.RAW_FILENAME[:-4] + '_3.' + custom.EXT, resize=(683, 384))
            setLights(180, 180, 0) ## yellow of same intensity
            camera.capture(custom.RAW_FILENAME[:-4] + '_4.' + custom.EXT, resize=(683, 384))

            snapshot = Image.new('RGBA', (1366, 768))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_1.' + custom.EXT).resize((683, 384)), (  0,   0,  683, 384))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_2.' + custom.EXT).resize((683, 384)), (683,   0, 1366, 384))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_3.' + custom.EXT).resize((683, 384)), (  0, 384,  683, 768))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_4.' + custom.EXT).resize((683, 384)), (683, 384, 1366, 768))
        elif effect == "Four":
            # take 4 photos and merge into one image.
            camera.capture(custom.RAW_FILENAME[:-4] + '_1.' + custom.EXT, resize=(683, 384))
            countdown(camera, can, custom.countdown2)
            camera.capture(custom.RAW_FILENAME[:-4] + '_2.' + custom.EXT, resize=(683, 384))
            countdown(camera, can, custom.countdown2)
            camera.capture(custom.RAW_FILENAME[:-4] + '_3.' + custom.EXT, resize=(683, 384))
            countdown(camera, can, custom.countdown2)
            camera.capture(custom.RAW_FILENAME[:-4] + '_4.' + custom.EXT, resize=(683, 384))

            snapshot = Image.new('RGBA', (1366, 768))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_1.' + custom.EXT).resize((683, 384)), (  0,   0,  683, 384))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_2.' + custom.EXT).resize((683, 384)), (683,   0, 1366, 384))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_3.' + custom.EXT).resize((683, 384)), (  0, 384,  683, 768))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_4.' + custom.EXT).resize((683, 384)), (683, 384, 1366, 768))
            
        camera.close()
            
    
        if custom.logo is not None:
            # snapshot.paste(logo,(0,SCREEN_H -lysize ),logo)
            # snapshot.paste(custom.logo,(SCREEN_W/2 - custom.logo.size[0]/2,
            #                             SCREEN_H -custom.lysize ),
            #                             custom.logo)
            size = snapshot.size
            logo_size = custom.logo.size
            yoff = size[1] - logo_size[1]
            xoff = (size[0] - logo_size[0]) // 2
            snapshot.paste(custom.logo,(xoff, yoff),
                           custom.logo)
        snapshot.save(custom.PROC_FILENAME)
    except Exception, e:
        print e
        snapshot = None
    return snapshot
snap.active = False


if custom.ARCHIVE: ### commented out... use custom.customizer instead
    # custom.archive_dir = tkFileDialog.askdirectory(title="Choose archive directory.", initialdir='/media/')
    if not os.path.exists(custom.archive_dir):
        print 'Directory not found.  Not archiving'
        custom.ARCHIVE = False
    elif not os.path.exists(custom.archive_dir): ## not used
        os.mkdir(custom.archive_dir)
    image_idx = len(glob.glob(os.path.join(custom.archive_dir, '%s_*.%s' % (custom.PROC_FILENAME[:-4], custom.EXT))))

SERIAL = None
def findser():
    global SERIAL
    if SERIAL is None: ## singleton
        SERIAL = serial.Serial('/dev/ttyS0',19200, timeout=.1)
        print 'using AlaMode'
    return SERIAL


def googleUpload(filen):
    #upload to picasa album
    if custom.albumID != 'None':
        album_url ='/data/feed/api/user/%s/albumid/%s' % (config.username, custom.albumID)
        photo = client.InsertPhotoSimple(album_url,'NoVa Snap',custom.photoCaption, filen ,content_type='image/jpeg')
    else:
        raise ValueError("albumID not set")
        
