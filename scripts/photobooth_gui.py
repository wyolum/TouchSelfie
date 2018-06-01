'''
Open source photo booth.

Kevin Osborn and Justin Shaw
WyoLum.com
'''

## imports
from tkkb import Tkkb
import time
from Tkinter import *
import tkMessageBox
import ImageTk
from mailfile import *
import custom
import Image
import config
from constants import *

## Hardware buttons interface
#       Will be used in "check_and_snap"
#       TODO move this in another module
import RPi.GPIO as GPIO

# BUTTON#_PIN are defined in constants.py
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

## This is a simple GUI, so we allow the root singleton to do the legwork
root = Tk()
root.attributes("-fullscreen",True)

# take a screenshot when <F12> is pressed
def screenshot(*args):
    import screenshot
    screenshot.snap()
root.bind('<F12>', screenshot)

### booth cam may need to present a file dialog gui.  So import after root is defined.
from boothcam import *

albumID_informed = False ### only show albumID customize info once

## put the status widget below the displayed image
STATUS_H_OFFSET = 150 ## was 210

## only accept button inputs from the AlaMode when ready
# TODO : remove
Button_enabled = False

import signal # remove ?
TIMEOUT = .3 # number of seconds your want for timeout

last_snap = time.time()


# On screen keyboard launch and kill
tkkb = None
def launch_tkkb(*args):
    '''
    Launch on screen keyboard program called tkkb-keyboard.
    install with '$ sudo apt-get install tkkb-keyboard'
    '''
    global tkkb
    if tkkb is None:
        tkkb = Toplevel(root)
        def onEnter(*args):
            kill_tkkb()
            sendPic()
        Tkkb(tkkb, etext, onEnter=onEnter)
        etext.config(state=NORMAL)
        tkkb.wm_attributes("-topmost", 1)
        tkkb.transient(root)
        tkkb_button.config(command=kill_tkkb, text="Close KB")
        tkkb.protocol("WM_DELETE_WINDOW", kill_tkkb)
        
def kill_tkkb():
    '''
    Delete on screen keyboard program called tkkb-keyboard.
    '''
    global tkkb
    if tkkb is not None:
        tkkb.destroy()
        try:
            tkkb_button.config(command=launch_tkkb, text="Open KB")
            tkkb = None
        except:
            pass

# Display the image on the center of the screen
def display_image(im=None):
    '''
    display image im in GUI window
    '''
    global image_tk
    
    # 1. Resize image to the screen size
    x,y = im.size
    print((x,y,SNAP_TO_SCREEN_SCALE))
    x = int(x / SNAP_TO_SCREEN_SCALE)
    y = int(y / SNAP_TO_SCREEN_SCALE)
    print( "x: %d, y:%d\n"%(x,y))
    im = im.resize((x,y));

    image_tk = ImageTk.PhotoImage(im)

    # 2. kill previous image if it exists and create a new one
    #     - delete all canvas elements with "image" in the tag
    can.delete("image")
    can.create_image([(SCREEN_W + x) / 2 - x/2,
                      0 + y / 2], 
                     image=image_tk, 
                     tags="image")

# helper function for timelapse photos (return true if capture needed)
def timelapse_due():
    '''
    Return true if a time lapse photo is due to be taken (see custom.TIMELAPSE)
    '''
    if custom.TIMELAPSE > 0:
        togo = custom.TIMELAPSE - (time.time() - last_snap)
        timelapse_label.config(text=str(int(togo)))
        out = togo < 0
    else:
        out = False
    return out

# helper function to periodically refresh Google oauth2 credentials
def refresh_oauth2_credentials():
    if custom.SIGN_ME_IN:
        if setup_google():
            print 'refreshed!', custom.oauth2_refresh_period
        else:
            print 'refresh failed'
        # reschedule me
        root.after(custom.oauth2_refresh_period, refresh_oauth2_credentials)

# Check if we should take a picture and do it if needed
def check_and_snap(force=False, countdown1=None):
    '''
    Check button status and snap a photo if button has been pressed.

    force -- take a snapshot regarless of button status
    countdown1 -- starting value for countdown timer
    '''
    global  image_tk, Button_enabled, last_snap, signed_in
    processed_file_name = custom.PROC_FILENAME
    processed_file_type = 'image/jpeg'
    
    if countdown1 is None:
        countdown1 = custom.countdown1
        
    # only allow send mail if we're connected to Google
    if signed_in:
        send_button.config(state=NORMAL)
        etext.config(state=NORMAL)
    else:
        send_button.config(state=DISABLED)
        etext.config(state=DISABLED)
    
    # Check for hardware button (priority from button 1 to button 3)
    hardware_button_state = 0
    if GPIO.input(BUTTON1_PIN) == BUTTON_IS_ACTIVE:
        hardware_button_state = 1
    elif GPIO.input(BUTTON2_PIN) == BUTTON_IS_ACTIVE:
        hardware_button_state = 2
    elif GPIO.input(BUTTON3_PIN) == BUTTON_IS_ACTIVE:
        hardware_button_state = 3
    # Here, hardware_button_state contains the state of the command
    # 0     -> no button pressed
    # 1,2,3 -> index of the button pressed
        
    if force or timelapse_due() or hardware_button_state != 0:
        ## take a photo and display it
        can.delete("text")
        can.update()
        
        if timelapse_due():
            # no countdown for timelapses
            countdown1 = 0
         
        if hardware_button_state == 1:
            # standard photo
            im = snap(can, countdown1=countdown1, effect='None')
        elif hardware_button_state == 2:
            # four photos
            im = snap(can, countdown1=countdown1, effect='Four')
        elif hardware_button_state == 3:
            # Gif animation
            im = snap(can, countdown1=countdown1, effect='Animation')
            # change processed image file name for upload
            processed_file_name = GIF_OUT_FILENAME 
            processed_file_type = "image/gif"
        else:
            # wasn't called from a hardware button, default behaviour
            im = snap(can, countdown1=countdown1, effect='None')

        # if we just shot an image, display it and upload it
        if im is not None:
            # If we're timelapsing, reset the number of millis to wait
            if custom.TIMELAPSE > 0:
                togo = custom.TIMELAPSE - (time.time() - last_snap)
            else:
                togo = 1e8
            last_snap = time.time()
            
            # display the picture we've just taken
            display_image(im)
            
            ## attempt to upload image
            # 1. show status
            can.delete("text")
            can.create_text(SCREEN_W/2, SCREEN_H - STATUS_H_OFFSET, text="Uploading Image", font=custom.CANVAS_FONT, tags="text")
            can.update()
            
            # 2. upload
            if signed_in:
                if custom.albumID == 'None':
                    global albumID_informed
                    if not albumID_informed:
                        tkMessageBox.showinfo('Album ID not set','Click Customize to select albumID', parent=root)
                        albumID_informed = True
                else:
                    try:
                        googleUpload(processed_file_name, mime_type = processed_file_type)
                    except Exception, e:
                        tkMessageBox.showinfo("Upload Error", str(e) + '\nUpload Failed:%s' % e)
            # 3. remove status
            can.delete("text")
            can.update()
    if not force:
        ## if this was a forced snapshot, exit, otherwise, call this function again in 100 ms
        root.after_id = root.after(100, check_and_snap)

## for clean shutdowns
root.after_id = None
def on_close(*args, **kw):
    '''
    when window closes cancel pending root.after() call
    '''
    if root.after_id is not None:
        root.after_cancel(root.after_id)
    ### exit GPIO
    GPIO.cleanup() 
    
    ### turn off LEDs
    r_var.set(0)
    g_var.set(0)
    b_var.set(0)
    root.quit()
root.protocol('WM_DELETE_WINDOW', on_close)

def force_snap(countdown1=None):
    if countdown1 is None:
        countdown1 = custom.countdown1
    check_and_snap(force=True, countdown1=countdown1)



#if they enter an email address send photo. add error checking
def sendPic(*args):
    if signed_in:
        print 'sending photo by email to %s' % email_addr.get()
        try:
            sendMail(email_addr.get().strip(),
                     custom.emailSubject,
                     custom.emailMsg,
                     custom.PROC_FILENAME)
            etext.delete(0, END)
            etext.focus_set()
            kill_tkkb()
        except Exception, e:
            print 'Send Failed::', e
            can.delete("all")
            can.create_text(SCREEN_W/2, SCREEN_H - STATUS_H_OFFSET, text="Send Failed", font=custom.CANVAS_FONT, tags="text")
            can.update()
            time.sleep(1)
            can.delete("all")
            im = Image.open(custom.PROC_FILENAME)
            display_image(im)
            can.create_text(SCREEN_W/2, SCREEN_H - STATUS_H_OFFSET, text="Press button when ready", font=custom.CANVAS_FONT, tags="text")
            can.update()
    else:
        print 'Not signed in'

def delay_timelapse(*args):
    '''
    Prevent a timelapse snapshot when someone is typeing an email address
    '''
    global last_snap
    last_snap = time.time()

#bound to text box for email
email_addr = StringVar()
email_addr.trace('w', delay_timelapse)


w, h = root.winfo_screenwidth(), root.winfo_screenheight()

# root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (SCREEN_W, SCREEN_H))
root.focus_set() # <-- move focus to this widget
frame = Frame(root)

# Button(frame, text="Exit", command=on_close).pack(side=LEFT)
Button(frame, text="Customize", command=lambda *args: custom.customize(root)).pack(side=LEFT)
tkkb_button = Button(frame, command=launch_tkkb, text="Launch-KB")
# tkkb_button.pack(side=LEFT)
send_button = Button(frame, text="SendEmail", command=sendPic, font=custom.BUTTON_FONT)
send_button.pack(side=RIGHT)

if custom.TIMELAPSE > 0:
    timelapse_label = Label(frame, text=custom.TIMELAPSE)
else:
    timelapse_label = Label(frame, text='')
timelapse_label.pack(side=LEFT)

## add a text entry box for email addresses
etext = Entry(frame,width=40, textvariable=email_addr, font=custom.BUTTON_FONT)
etext.pack()
frame.pack()
etext.bind('<Button-1>', launch_tkkb)

def labeled_slider(parent, label, from_, to, side, variable):
    frame = Frame(parent)
    Label(frame, text=label).pack(side=TOP)
    scale = Scale(frame, from_=from_, to=to, variable=variable, resolution=1).pack(side=TOP)
    frame.pack(side=side)
    return scale

## add a software button in case hardware button is not available
interface_frame = Frame(root)

snap_button = Button(interface_frame, text="snap", command=force_snap, font=custom.BUTTON_FONT)
# snap_button.pack(side=RIGHT) ## moved to canvas
interface_frame.pack(side=RIGHT)

## the canvas will display the images
can = Canvas(root, width=SCREEN_W, height=SCREEN_H)
can.pack()
def snap_callback(*args):
    force_snap()
can.bind('<Button-1>', snap_callback)

## sign in to google?
if custom.SIGN_ME_IN:
    signed_in = setup_google()
else:
    signed_in = False
if not signed_in:
    send_button.config(state=DISABLED)
    etext.config(state=DISABLED)

### take the first photo (no delay)
can.delete("text")
can.create_text(SCREEN_W/2, SCREEN_H/2, text="SMILE ;-)", font=custom.CANVAS_FONT, tags="splash")
can.update()
force_snap(countdown1=0)

### check button after waiting for 200 ms
root.after(200, check_and_snap)
if custom.SIGN_ME_IN:
    root.after(custom.oauth2_refresh_period, refresh_oauth2_credentials)
root.wm_title("Wyolum Photobooth")
etext.focus_set()

root.mainloop()


