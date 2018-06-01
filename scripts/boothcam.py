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

from credentials import OAuth2Login

from PIL import Image
import config
import custom
import httplib2

from constants import * 


# This will be called during the final moment of countdown() or countdown1()
# This works out of the box with Picamera V1, change the code to blink something
# if you have the hardware
def safe_set_led(camera, state):
    try:
        camera.led = state
    except:
        pass

# Connection to Google for Photo album upload
def setup_google():
    global client
    try:
        # Create a client class which will make HTTP requests with Google Docs server.
        configdir = os.path.expanduser('./')
        client_secrets = os.path.join(configdir, 'OpenSelfie.json')
        credential_store = os.path.join(configdir, 'credentials.dat')
        client = OAuth2Login(client_secrets, credential_store, config.username)
	return True
    except KeyboardInterrupt:
        raise
    except Exception, e:
        print 'could not login to Google, check .credential file\n   %s' % e
        return False
    
# This starts the preview with transparency and display a countdown on the canvas
# set canvas font (for countdown() only)
font = (COUNTDOWN_FONT_FAMILY, COUNTDONW_FONT_SIZE)
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

# overlay generation mechanism for bounding boxes
from PIL import ImageDraw
def bbox_overlay(camera, bbox = None):
    MASK_ALPHA = 127	
    if bbox is None:
	bbox = (0.0, 0.0, 1.0, 1.0) # full bbox
	
    preview_window_size = camera.preview_window #(x,y,w,h)
    ov_w = preview_window[2]
    ov_h = preview_window[3]
    overlay = Image.new('RGBA', (ov_w, ov_h))
    # compute bounding box in pixels
    ulx = int( bbox[0] * ov_w )
    brx = int( (bbox[0] + bbox[2]) * ov_w) +1
    uly = int( bbox[1] * ov_h)
    bry = int( (bbox[1] + bbox[3]) * ov_h) +1
    # Draw obscuring rectangles
    draw = ImageDraw.Draw(overlay)
    # fill with transluscency
    draw.rectangle(((0,0),(ov_w, ov_h)), fill = (0, 0, 0, MASK_ALPHA))	
    # show the bbox
    draw.rectangle(((ulx, uly), (brx, bry)), fill=(0,0,0,0))
    # add the overlay
    o = camera.add_overlay(overlay.tostring(), size=(ov_w, ov_h))
    o.layer = 3 # move above the display
    return o


# This is identical to the previous function but uses text_annotate instead with opaque preview
def countdown2(camera, can, countdown1):
    camera.start_preview()
    camera.preview_alpha = 255 # Opaque preview
    # camera.start_preview(fullscreen=False,
    #                     crop=(50, 150, 800, 480),
    #                      window=(0, 0, 800, 480),
    #                      hflip=True)
    can.delete("image") # Maybe useless (opaque preview)
    ovl = bbox_overlay(camera,(0.3, 0.3, 0.5, 0.5))
    led_state = False
    safe_set_led(camera, led_state)

    # Use annotation text instead of text for countdown
    camera.annotate_size = 160 # Maximum size
    camera.annotate_foreground = Color('white')
    camera.annotate_background = Color('black')
    camera.annotate_text = "" # Remove annotation
    
    camera.preview_window = (0, 0, SCREEN_W, SCREEN_H)
    camera.preview_fullscreen = False

    can.delete("all") # Useless ?
    
    #Change text every second and blink led
    for i in range(countdown1):
	# Annotation text
	camera.annotate_text = "  " + str(countdown1 - i) + "  "
        if i < countdown1 - 2:
	    # slow blink until -2s
            time.sleep(1)
            led_state = not led_state
            safe_set_led(camera, led_state)
        else:
	    # fast blink until the end
            for j in range(5):
                time.sleep(.2)
                led_state = not led_state
                safe_set_led(camera, led_state)
    camera.annotate_text = ""
    camera.remove_overlay(ovl)
    camera.stop_preview()

# Take a snapshot (or a succession of snapshots), process it, archive it and return it
def snap(can, countdown1, effect='None'):
    global image_idx
    try:
	# Should we archive the previous processed image ?
        if custom.ARCHIVE and os.path.exists(custom.archive_dir): 
	    # if previous image exists
            if os.path.exists(custom.PROC_FILENAME):
                ### move image to archive
                image_idx += 1
                new_filename = os.path.join(custom.archive_dir, '%s_%05d.%s' % (custom.PROC_FILENAME[:-4], image_idx, custom.EXT))
                command = (['mv', custom.PROC_FILENAME, new_filename])
                call(command)
	    # if previous animation exists	
            elif os.path.exists(GIF_OUT_FILENAME):
                ### move animation to archive
                image_idx += 1
                new_filename = os.path.join(custom.archive_dir, 'animation_%05d.gif' % (image_idx))
                command = (['mv', GIF_OUT_FILENAME, new_filename])
                call(command)
	# start camera
        camera = mycamera.PiCamera()
        
	#Start countdown
	#countdown(camera, can, countdown1) # Use countdown2() instead
	countdown2(camera, can, countdown1)
	
        # take pictures and process them based on 'effect'
	# in the end, 'snapshot' must contain the processed image
	if effect == 'None':
	    # simple snapshot
            camera.capture(custom.RAW_FILENAME, resize=(SNAP_W, SNAP_H))
            snapshot = Image.open(custom.RAW_FILENAME)
        
        elif effect == "Four":
	    # collage of four pictures
	
	    # compute the half sizes
            w = int(SNAP_W/2)
            h = int(SNAP_H/2)

	    # take 4 photos and merge into one image.
            camera.capture(custom.RAW_FILENAME[:-4] + '_1.' + custom.EXT, resize=(w, h))
            countdown2(camera, can, custom.countdown2) # briever pause
            camera.capture(custom.RAW_FILENAME[:-4] + '_2.' + custom.EXT, resize=(w, h))
            countdown2(camera, can, custom.countdown2)
            camera.capture(custom.RAW_FILENAME[:-4] + '_3.' + custom.EXT, resize=(w, h))
            countdown2(camera, can, custom.countdown2)
            camera.capture(custom.RAW_FILENAME[:-4] + '_4.' + custom.EXT, resize=(w, h))

	    # collage
            snapshot = Image.new('RGBA', (1366, 768))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_1.' + custom.EXT).resize((w, h)), (  0,   0,  w, h))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_2.' + custom.EXT).resize((w, h)), (w,   0, SNAP_W, h))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_3.' + custom.EXT).resize((w, h)), (  0, h,  w, SNAP_H))
            snapshot.paste(Image.open(custom.RAW_FILENAME[:-4] + '_4.' + custom.EXT).resize((w, h)), (w, h, SNAP_W, SNAP_H))
	    #paste the collage enveloppe if it exists
	    try:
	        front = Image.open(COLLAGE_FRONT_ENVELOPPE)
		snapshot.paste(front, (0, 0 , SNAP_W, SNAP_H))
	    except:
		pass
	# GIF Animation
        elif effect == "Animation":
            # below is taken from official PiCamera doc and adapted
	
	    # take GIF_FRAME_NUMBER pictures resize to GIF_SIZE
            for i, filename in enumerate(camera.capture_continuous('animframe-{counter:03d}.jpg', resize= GIF_SIZE)):
                # print(filename)
		# TODO : enqueue the filenames and use that in the command line
                time.sleep(GIF_ACQ_INTERFRAME_DELAY_MILLIS / 1000.0)
                if i == GIF_FRAMES_NUMBER:
                    break
	    # Assemble images using image magick
            command_string = "convert -delay " + str(GIF_INTERFRAME_DELAY_MILLIS) + " " + "animframe-*.jpg " + GIF_OUT_FILENAME 
            os.system(command_string)
            snapshot = Image.open(GIF_OUT_FILENAME)
            #os.system("rm ./*.jpg") # cleanup source images
        
	# We're done using the camera
        camera.close()
            
	# Add a logo if it's been configured
	# TODO : move this to effect == "None" above since it's only used there
        if effect == "None" :   
            if custom.logo is not None :
                size = snapshot.size
                #resize logo to the wanted size
                custom.logo.thumbnail((LOGO_MAX_SIZE,LOGO_MAX_SIZE)) 
                logo_size = custom.logo.size

                #put logo on bottom right with padding
                yoff = size[1] - logo_size[1] - LOGO_PADDING
                xoff = size[0] - logo_size[0] - LOGO_PADDING
                snapshot.paste(custom.logo,(xoff, yoff), custom.logo)

            snapshot.save(custom.PROC_FILENAME)
            
    except Exception, e:
        print e
        snapshot = None
    return snapshot

snap.active = False # Remove ?

# initialize picture archive path and picture index
if custom.ARCHIVE: ### commented out... use custom.customizer instead
    # custom.archive_dir = tkFileDialog.askdirectory(title="Choose archive directory.", initialdir='/media/')
    if not os.path.exists(custom.archive_dir):
        print 'Directory not found.  Not archiving'
        custom.ARCHIVE = False
    image_idx = len(glob.glob(os.path.join(custom.archive_dir, '%s_*.%s' % (custom.PROC_FILENAME[:-4], custom.EXT))))

def googleUpload(filen, title='Photobooth photo', caption = None, mime_type='image/jpeg'):
    #upload to picasa album
    if caption  is None:
        caption = custom.photoCaption
    if custom.albumID != 'None':
        album_url ='/data/feed/api/user/%s/albumid/%s' % (config.username, custom.albumID)
        photo = client.InsertPhotoSimple(album_url, title, caption, filen ,content_type=mime_type)
    else:
        raise ValueError("albumID not set")
        
