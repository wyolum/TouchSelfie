"""
New interface for the photobooth

@author: Laurent Alacoque 2o18
"""

from Tkinter import *
import tkMessageBox
from PIL import ImageTk,Image
#from tkkb import Tkkb
from mykb import TouchKeyboard
from tkImageLabel import ImageLabel
from constants import *
import time
import traceback

import os
import subprocess

import oauth2services

try:
    import hardware_buttons as HWB
except ImportError:
    print "Error importing hardware_buttons, using fakehardware instead"
    print traceback.print_exc()
    import fakehardware as HWB
    
try:
    import picamera as mycamera
    from picamera.color import Color
except ImportError:
    print "picamera not found, trying cv2_camera"
    try:
        import cv2_camera as mycamera
    except ImportError:
        print "cv2_camera import failed : using fake hardware instead"
        import fakehardware as mycamera
        from fakehardware import Color

# Helper class to launch function after a long-press
class LongPressDetector:
    """Helper class that calls a callback after a long press/click"""
# call_back will get the long_click duration as parameter
    def __init__(self, root, call_back, long_press_duration = 1000 ):
        """Creates the LongPressDetector
        
        Arguments:
            root (Tk Widget): parent element for the event binding
            call_back       : a callback function with prototype callback(press_duration_ms)
            long_press_duration : amount of milliseconds after which we consider this press is long
        """
        self.ts=0
        self.root = root
        self.call_back = call_back
        self._suspend = False
        self.long_press_duration = long_press_duration
        root.bind("<Button-1>",self.__click)
        root.bind("<ButtonRelease-1>",self.__release)
        
        # Suspend actions in case we loose focus or leave 
        root.bind("<FocusOut>",self.__suspend)
        root.bind("<Leave>",self.__suspend)
        # Reactivate actions in case we're back
        root.bind("<FocusIn>",self.__continue)
        root.bind("<Enter>",self.__continue)
       
    def __suspend(self,event):
        """suspend longpress action"""
        self._suspend = True
    
    def __continue(self,event):
        """reactivate longpress action"""
        self._suspend = False
        self.ts = event.time
        
    def __click(self,event):
        self.ts = event.time

    def __release(self,event):
        if self._suspend:
            #cancel this event
            print "suspended"
            self._suspend = False
            return
        duration = event.time - self.ts
        if self.call_back != None and duration > self.long_press_duration:
            self.call_back(duration)

class UserInterface():
    """A User Interface for the photobooth"""
    def __init__(self, config, window_size=None, poll_period=HARDWARE_POLL_PERIOD):
        """Constructor for the UserInterface object
        
        Arguments:
            config (configuration.Configuration()) : the configuration object
            window_size  tupple(w,h) : the window size (defaults to size in constants.py)
            poll_period : polling period for hardware buttons changes (ms)
        """
        upload_images = config.enable_upload
        send_emails   = config.enable_email
        hardware_buttons = config.enable_hardware_buttons
        
        self.root = Tk()

        ## Auto hide Mouse cursor

        #Events to enable/disable cursor based on motion
        #on_motion() is called on mouse motion and sets a boolean
        #enable_cursor is a fast loop that checks this boolean and enable the cursor
        #check_and_disable_cursor is a slow loop that checks this boolean and resets it
        self.cursor_motion = False
        def enable_cursor():
            if self.cursor_motion:
                self.root.config(cursor="")
            self.enable_cursor_after_id = self.root.after(200,enable_cursor)
        def check_and_disable_cursor():
            if self.cursor_motion == False:
                #remove the cursor,reactivated by motion
                self.root.config(cursor="none")
            else:
                #erase it
                self.cursor_motion = False
            self.disable_cursor_after_id = self.root.after(3000,check_and_disable_cursor)
        def on_motion(event):
            self.cursor_motion = True
        self.root.bind("<Motion>",on_motion)
        self.enable_cursor_after_id = self.root.after(100,enable_cursor)
        self.disable_cursor_after_id = self.root.after(2000,check_and_disable_cursor)
        ## End of Auto-hide mouse cursor

        ## Bind keyboard keys to actions
        def install_key_binding(action,function):
            if action in ACTIONS_KEYS_MAPPING.keys():
                for key in ACTIONS_KEYS_MAPPING[action]:
                    self.root.bind(key,function) 
        install_key_binding("snap_None",lambda *args: self.snap("None"))
        install_key_binding("snap_Four",lambda *args: self.snap("Four"))
        install_key_binding("snap_Animation",lambda *args: self.snap("Animation"))
        install_key_binding("send_email",lambda *args: self.send_email())
        install_key_binding("configure",lambda *args: self.long_press_cb(self))
        ## Bind keyboard keys to actions

        if config.full_screen:
            self.root.attributes("-fullscreen",True)
        
        self.root.configure(background='black')
        if window_size is not None:
            self.size=window_size
        else:
            self.size=(640,480)
        
        self.root.geometry('%dx%d+0+0'%(self.size[0],self.size[1]))

        #Configure Image holder
        self.image = ImageLabel(self.root, size=self.size)
        self.image.place(x=0, y=0, relwidth = 1, relheight=1)
        self.image.configure(background='black')
     
        self.send_emails = send_emails
        #Create sendmail Button
        if self.send_emails:
            mail_image = Image.open(EMAIL_BUTTON_IMG)
            w,h = mail_image.size
            self.mail_imagetk = ImageTk.PhotoImage(mail_image)
            self.mail_btn  = Button(self.root,image = self.mail_imagetk, height=h, width=w, command=self.send_email )
            self.mail_btn.place(x=SCREEN_W-w-2, y=0)
            self.mail_btn.configure(background = 'black')
        
        #Create status line
        self.status_lbl = Label(self.root, text="", font=("Helvetica", 20))
        self.status_lbl.config(background='black', foreground='white')
        self.status_lbl.place(x=0 + 10, y=0)
        
        #State variables
        self.signed_in = False
        self.auth_after_id = None
        self.poll_period = poll_period
        self.poll_after_id = None
        
        self.last_picture_filename = None
        self.last_picture_time = time.time()
        self.last_picture_mime_type = None
        
        self.tkkb = None
        self.email_addr = StringVar()
        
        self.suspend_poll = False
        
        self.upload_images = upload_images
        self.account_email = config.user_name
        self.send_emails = send_emails
        self.upload_images = upload_images
        self.config = config
        #Google credentials

        self.configdir = os.path.expanduser('./')
        self.oauth2service = oauth2services.OAuthServices(
            os.path.join(self.configdir, APP_ID_FILE),
            os.path.join(self.configdir, CREDENTIALS_STORE_FILE),
            self.account_email,
            enable_email = send_emails,
            enable_upload = upload_images)
        
        #Hardware buttons
        if hardware_buttons:
            self.buttons = HWB.Buttons( buttons_pins = HARDWARE_BUTTONS['button_pins'], mode = HARDWARE_BUTTONS["pull_up_down"], active_state = HARDWARE_BUTTONS["active_state"])
        else:
            self.buttons = HWB.Buttons( buttons_pins = [], mode=0, active_state=0)
        
        if not self.buttons.has_buttons():
            #oh oh, we don't have hardware buttons, create soft ones
            print "No hardware buttons found, generating software buttons"
            
            self.software_buttons_images = {}
            self.software_buttons = []
            X_ = 0
            total_width = 0
            # first, open images and load them + compute the total width
            for i, effect in enumerate(SOFTWARE_BUTTONS):
                effect_image = Image.open(SOFTWARE_BUTTONS[effect]['icon'])
                w,h = effect_image.size
                tkimage = ImageTk.PhotoImage(effect_image)
                self.software_buttons_images[effect] = {}
                self.software_buttons_images[effect]['image'] = tkimage
                self.software_buttons_images[effect]['size'] = (w,h)
                total_width = total_width + w
            #we have the total size, compute padding
            padding = int((self.size[0] - total_width) / (len(SOFTWARE_BUTTONS) - 1))
            # decurrying of callback parameter
            def snap_factory(effect):
                return lambda *args:self.snap(effect)
                
            for i, effect in enumerate(SOFTWARE_BUTTONS):
                #print effect, SOFTWARE_BUTTONS[effect]
                effect_image = Image.open(SOFTWARE_BUTTONS[effect]['icon'])
                w,h = self.software_buttons_images[effect]['size']
                Y = self.size[1] - h
                tkimage = self.software_buttons_images[effect]['image']

                btn = Button(self.root, image=tkimage, width = w, height= h, command=snap_factory(effect))
                self.software_buttons.append(btn)
                btn.place(x=X_,y=Y)
                btn.configure(background = 'black')
                X_ = X_ + w + padding
        
        #Camera
        self.camera = mycamera.PiCamera()
        self.camera.annotate_text_size = 160 # Maximum size
        self.camera.annotate_foreground = Color('white')
        self.camera.annotate_background = Color('black')

        #Callback for long-press on screen
        def long_press_cb(time):
            #Create a toplevel window with checkboxes and a "Quit application button"
            top = Toplevel(self.root)
            qb = Button(top,text="Quit Application",command=self.root.destroy)
            qb.pack(pady=20)

            mail_enable = IntVar()
            upload_enable = IntVar()
            if self.send_emails: mail_enable.set(1)
            else: mail_enable.set(0) 
            if self.upload_images: upload_enable.set(1)
            else: upload_enable.set(0) 

            me = Checkbutton(top, text="Enable Email sending", variable=mail_enable,anchor=W)
            me.pack(padx=20,pady=10,fill=X)
            ue = Checkbutton(top, text="Enable Uploading", variable=upload_enable,anchor=W)
            ue.pack(padx=20,pady=10,fill=X)
            
            def ok():
                enable_email = (mail_enable.get() != 0)
                enable_upload = (upload_enable.get() != 0)
                self.__change_services(enable_email,enable_upload)
                top.destroy()

            b=Button(top, text="OK", command=ok)
            b.pack(pady=20)
            self.root.wait_window(top) 




        self.long_press_cb= long_press_cb
        self.longpress_obj= LongPressDetector(self.root,long_press_cb)

    def __change_services(self,email,upload):
        """Called whenever we should change the state of oauth2services"""
        self.oauth2service.enable_email = email
        self.oauth2service.enable_upload = upload
        self.send_emails = email
        self.upload_images = upload
        #TODO show/hide button = oauth2services.OAuthServices(
        if email:
            self.mail_btn.configure(state=NORMAL)
        else:
            self.mail_btn.configure(state=DISABLED)
        
    
    def __del__(self):
        """Destructor"""
        try:
            self.root.after_cancel(self.auth_after_id)
            self.root.after_cancel(self.poll_after_id)
            self.camera.close()
        except:
            pass
        
    def status(self, status_text):
        """Update the application status line with status_text"""
        self.status_lbl['text'] = status_text
        self.root.update()
    
    def start_ui(self):
        """Start the user interface and call Tk::mainloop()"""
        self.auth_after_id = self.root.after(100, self.refresh_auth)
        self.poll_after_id = self.root.after(self.poll_period, self.run_periodically)
        self.root.mainloop()

        
    def run_periodically(self):
        """hardware poll function launched by start_ui"""
        if not self.suspend_poll == True:
            self.status('')
            btn_state = self.buttons.state()
            if btn_state == 1:
                self.snap("None")
            elif btn_state == 2:
                self.snap("Four")
            elif btn_state == 3:
                self.snap("Animation")
        self.poll_after_id = self.root.after(self.poll_period, self.run_periodically)

    def snap(self,mode="None"):
        """Snap a shot in given mode
        
        This will start a countdown preview and:
            - take snapshot(s)
            - process them
            - archive them locally
            - upload them to Google Photos
        
        Arguments:
            mode ("None"|"Four"|"Animation") : the selected mode
        """
        print "snap (mode=%s)" % mode
        self.suspend_poll = True
        # clear status
        self.status("")
        
        if mode not in EFFECTS_PARAMETERS.keys():
            print "Wrong mode %s defaults to 'None'" % mode
            mode = "None"
        
        #hide backgroud image
        self.image.unload()

        # update this to be able to send email and upload
        # snap_filename = snap_picture(mode)
        # take a snapshot here
        snap_filename = None
        snap_size = EFFECTS_PARAMETERS[mode]['snap_size']
        try:
            # 1. Start Preview
            self.camera.resolution = snap_size
            self.camera.start_preview()
            # 2. Show initial countdown
            # 3. Take snaps and combine them
            if mode == 'None':
                self.__show_countdown(config.countdown1,annotate_size = 160)
                # simple shot with logo
                self.camera.capture('snapshot.jpg')
                self.camera.stop_preview()
            
                snapshot = Image.open('snapshot.jpg')
                if config.logo_file is not None :
                    config.logo = Image.open(config.logo_file)
                    size = snapshot.size
                    #resize logo to the wanted size
                    config.logo.thumbnail((EFFECTS_PARAMETERS['None']['logo_size'],EFFECTS_PARAMETERS['None']['logo_size'])) 
                    logo_size = config.logo.size
                    #put logo on bottom right with padding
                    yoff = size[1] - logo_size[1] - EFFECTS_PARAMETERS['None']['logo_padding']
                    xoff = size[0] - logo_size[0] - EFFECTS_PARAMETERS['None']['logo_padding']
                    snapshot.paste(config.logo,(xoff, yoff), config.logo)
                snapshot.save('snapshot.jpg')
                snap_filename = 'snapshot.jpg'
                self.last_picture_mime_type = 'image/jpg'
                
            elif mode == 'Four':
                # collage of four shots
                # compute collage size
                w = snap_size[0]
                h = snap_size[1]
                w_ = w * 2
                h_ = h * 2
                # take 4 photos and merge into one image.
                self.__show_countdown(config.countdown1,annotate_size = 80)
                self.camera.capture('collage_1.jpg')
                self.__show_countdown(config.countdown2,annotate_size = 80)
                self.camera.capture('collage_2.jpg')
                self.__show_countdown(config.countdown2,annotate_size = 80)
                self.camera.capture('collage_3.jpg')
                self.__show_countdown(config.countdown2,annotate_size = 80)
                self.camera.capture('collage_4.jpg')
                # Assemble collage
                self.camera.stop_preview()
                self.status("Assembling collage")
                snapshot = Image.new('RGBA', (w_, h_))
                snapshot.paste(Image.open('collage_1.jpg'), (  0,   0,  w, h))
                snapshot.paste(Image.open('collage_2.jpg'), (w,   0, w_, h))
                snapshot.paste(Image.open('collage_3.jpg'), (  0, h,  w, h_))
                snapshot.paste(Image.open('collage_4.jpg'), (w, h, w_, h_))
                #paste the collage enveloppe if it exists
                try:
                    front = Image.open(EFFECTS_PARAMETERS[mode]['foreground_image'])
                    front = front.resize((w_,h_))
                    front = front.convert('RGBA')
                    snapshot = snapshot.convert('RGBA')
                    #print snapshot
                    #print front
                    snapshot=Image.alpha_composite(snapshot,front)

                except Exception, e:
                    traceback.print_exc()

                self.status("")
                snapshot = snapshot.convert('RGB')
                snapshot.save('collage.jpg')
                snap_filename = 'collage.jpg'
                self.last_picture_mime_type = 'image/jpg'
                
            elif mode == 'Animation':
                # animated gifs
                # below is taken from official PiCamera doc and adapted
                # take GIF_FRAME_NUMBER pictures resize to GIF_SIZE
                self.__show_countdown(config.countdown1,annotate_size = 50)
                for i, filename in enumerate(self.camera.capture_continuous('animframe-{counter:03d}.jpg')):
                    # print(filename)
                    # TODO : enqueue the filenames and use that in the command line
                    time.sleep(EFFECTS_PARAMETERS[mode]['snap_period_millis'] / 1000.0)
                    # preload first frame because convert can be slow
                    if i == 0: 
                        print "changing " + filename
                        self.image.load(str(filename))
                    if i >= EFFECTS_PARAMETERS[mode]['frame_number']:
                        break
                self.camera.stop_preview()
                
                # Assemble images using image magick
                self.status("Assembling animation")
                command_string = "convert -delay " + str(EFFECTS_PARAMETERS[mode]['gif_period_millis']) + " animframe-*.jpg animation.gif"
                os.system(command_string)
                self.status("")
                snap_filename = 'animation.gif'
                self.last_picture_mime_type = 'image/gif'
            
            # Here, the photo or animation is in snap_filename
            if os.path.exists(snap_filename):
                self.last_picture_filename = snap_filename
                self.last_picture_time = time.time()
                self.last_picture_timestamp = time.strftime("%Y-%m-%d_%H-%M-%S",time.gmtime())
                self.last_picture_title = time.strftime("%d/%m/%Y %H:%M:%S",time.gmtime()) #TODO add event name
                
                # 1. Display
                self.image.load(snap_filename)
                # 2. Upload
                if self.signed_in:
                    self.status("Uploading image")
                    self.googleUpload(
                        self.last_picture_filename, 
                        title= self.last_picture_title,
                        caption = config.photoCaption + " " + self.last_picture_title)
                    self.status("")
                # 3. Archive
                if config.ARCHIVE:
                    if os.path.exists(config.archive_dir):
                        new_filename = ""
                        if mode == 'None':
                            new_filename = "%s-snap.jpg" % self.last_picture_timestamp
                        elif mode == 'Four':
                            new_filename = "%s-collage.jpg" % self.last_picture_timestamp
                        elif mode == 'Animation':
                            new_filename = "%s-anim.gif" % self.last_picture_timestamp
                            
                        new_filename = os.path.join(config.archive_dir,new_filename)
                        os.rename(self.last_picture_filename, new_filename)
                        self.last_picture_filename = new_filename
                    else:
                        print "Error : archive_dir %s doesn't exist"% config.archive_dir


            else:
                # error
                self.status("Snap failed :(")
                self.image.unload()
        except Exception, e:
            print e
            traceback.print_exc()
            snapshot = None
        self.suspend_poll = False    
        return snap_filename

    def __countdown_set_led(self,state):
        ''' if you have a hardware led on the camera, link it to this'''
        try:
            self.camera.led = state
        except:
            pass
            
    def __show_countdown(self,countdown,annotate_size=160):
        '''wrapper function to select between overlay and text countdowns'''
        #self.__show_text_countdown(countdown,annotate_size=annotate_size)
        self.__show_overlay_countdown(countdown)
        
    def __show_text_countdown(self,countdown,annotate_size=160):
        ''' display countdown. the camera should have a preview active and the resolution must be set'''
        led_state = False
        self.__countdown_set_led(led_state)

        self.camera.annotate_text = "" # Remove annotation
        self.camera.annotate_text_size = annotate_size
        #self.camera.preview.window = (0, 0, SCREEN_W, SCREEN_H)
        self.camera.preview.fullscreen = True

        #Change text every second and blink led
        for i in range(countdown):
            # Annotation text
            self.camera.annotate_text = "  " + str(countdown - i) + "  "
            if i < countdown - 2:
            # slow blink until -2s
                time.sleep(1)
                led_state = not led_state
                self.__countdown_set_led(led_state)
            else:
            # fast blink until the end
                for j in range(5):
                    time.sleep(.2)
                    led_state = not led_state
                    self.__countdown_set_led(led_state)
        self.camera.annotate_text = ""
    
    def __show_overlay_countdown(self,countdown):
        """Display countdown as images overlays"""
        #COUNTDOWN_OVERLAY_IMAGES
        led_state = False
        self.__countdown_set_led(led_state)

        self.camera.preview.fullscreen = True
        self.camera.preview.hflip = True  #Mirror effect for easier selfies
        #for some reason camera.preview.window =(0,0,0,0)
        #bbox = self.camera.preview.window
        #preview_width = bbox[2]
        #preview_height = bbox[3]
        preview_size = self.camera.resolution
        preview_width = preview_size[0]
        preview_height = preview_size[1]
        
        overlay_height = int(preview_height * 0.2)
        print preview_size
        print preview_width, preview_height, overlay_height
        
        ## prepare overlay images (resize)
        overlay_images = []
        for i in range(countdown):
            if i >= len(COUNTDOWN_OVERLAY_IMAGES):
                break;
            #read overlay image
            im = Image.open(COUNTDOWN_OVERLAY_IMAGES[i])
            #resize to 20% of height
            im.thumbnail((preview_width,overlay_height))
            
            #overlays should be padded to 32 (width) and 16 (height)
            pad_width = int((preview_width + 31) / 32) * 32
            pad_height = int((preview_height + 15) / 16) * 16
            
            padded_overlay = Image.new('RGBA', (pad_width, pad_height))
            # Paste the original image into the padded one (centered)
            padded_overlay.paste(im, ( int((preview_width+im.size[0])/2.0), int((preview_height+im.size[1])/2.0)))
            overlay_images.append(padded_overlay)
        ## All images loaded at the right resolution

        #Change overlay every second and blink led
        for i in range(countdown):
            #what overlay image to select:
            overlay_image = None
            overlay_image_num = countdown -1 -i #5-1-0 ==> 4 ; 5-1-4 ==> 0
            if overlay_image_num >= len(overlay_images):
                overlay_image = overlay_images[len(overlay_images)-1]
            elif overlay_image_num < 0:
                overlay_image = None
            else:
                overlay_image = overlay_images[overlay_image_num]
            ## Add overlay to image
            overlay = None
            if overlay_image != None:
                #create overlay
                overlay = self.camera.add_overlay(overlay_image.tobytes(), size=overlay_image.size)
                #move it on top of preview
                overlay.layer = 3
                #change transparency
                overlay.alpha = 128
                #flip it horizontally (because preview is flipped)
                #overlay.hflip = True
            
            if i < countdown - 2:
            # slow blink until -2s
                time.sleep(1)
                led_state = not led_state
                self.__countdown_set_led(led_state)
            else:
            # fast blink until the end
                for j in range(5):
                    time.sleep(.2)
                    led_state = not led_state
                    self.__countdown_set_led(led_state)
            if overlay != None:
                self.camera.remove_overlay(overlay)
                
        
        
    def refresh_auth(self):
        """ refresh the oauth2 service (regularly called)"""
        # useless if we don't need image upload
        if not self.upload_images:
            if self.send_emails:
                self.signed_in = True #Will fail otherwise
                self.mail_btn.configure(state=NORMAL)
            return
        # actual refresh
        if self.oauth2service.refresh():
            if self.send_emails:
                self.mail_btn.configure(state=NORMAL)
            self.signed_in = True
        else:
            if self.send_emails:        
                self.mail_btn.configure(state=DISABLED)
            self.signed_in = False
            print 'refresh failed'

        #relaunch periodically
        self.auth_after_id = self.root.after(OAUTH2_REFRESH_PERIOD, self.refresh_auth)
        
            
    def googleUpload(self,filen, title='Photobooth photo', caption = None):
        """Upload a picture to Google Photos
        
        Arguments:
            filen (str) : path to the picture to upload
            title       : title of the picture
            caption     : optional caption for the picture
        """
        if not self.upload_images:
            return
        #upload to picasa album
        if caption is None:
            caption = config.photoCaption
        if config.albumID == 'None':
            config.albumID = None
        
        self.oauth2service.upload_picture(filen, config.albumID, title, caption)
        
            
    def send_email(self):
        """Ask for an email address and send the last picture to it
        
        This will popup a touch keyboard
        """
        if not self.send_emails:
            return
        if self.signed_in and self.tkkb is None:
            self.email_addr.set("")
            self.suspend_poll = True
            self.longpress_obj.suspend() # solves bug of longpress detected when keyboard was displayed
            self.tkkb = Toplevel(self.root)
            keyboard_parent = self.tkkb
            consent_var = IntVar()
            if self.config.enable_email_logging:
                #build consent control
                main_frame=Frame(self.tkkb)
                consent_frame = Frame(self.tkkb, bg='white', pady=20)
                consent_var.set(1)
                consent_cb = Checkbutton(consent_frame,text="Ok to log my mail address", variable=consent_var, font="Helvetica",bg='white', fg='black')
                consent_cb.pack(fill=X)
                consent_frame.pack(side=BOTTOM,fill=X)
                main_frame.pack(side=TOP,fill=Y)
                keyboard_parent=main_frame
                def onEnter(*args):
                    self.kill_tkkb()
                    res = self.__send_picture()
                    self.__log_email_address(self.email_addr.get(),consent_var.get()!=0, res, self.last_picture_filename)
                TouchKeyboard(keyboard_parent,self.email_addr, onEnter = onEnter)
                self.tkkb.wm_attributes("-topmost", 1)
                self.tkkb.transient(self.root)
                self.tkkb.protocol("WM_DELETE_WINDOW", self.kill_tkkb)
                    
            else:
                def onEnter(*args):
                    self.kill_tkkb()
                    self.__send_picture()

                TouchKeyboard(keyboard_parent,self.email_addr, onEnter = onEnter)
                self.tkkb.wm_attributes("-topmost", 1)
                self.tkkb.transient(self.root)
                self.tkkb.protocol("WM_DELETE_WINDOW", self.kill_tkkb)
            
    def kill_tkkb(self):
        """Kill the popup keyboard"""
        if self.tkkb is not None:
            self.tkkb.destroy()
            self.tkkb = None
            self.suspend_poll = False
            
    def __send_picture(self):
        """Actual code to send picture self.last_picture_filename by email to the address entered in self.email_addr StringVar"""
        if not self.send_emails:
            return False
        retcode = False
        if self.signed_in:
            #print 'sending photo by email to %s' % self.email_addr.get()
            self.status("Sending Email")
            try:
                retcode = self.oauth2service.send_message(
                    self.email_addr.get().strip(),
                    config.emailSubject,
                    config.emailMsg,
                    self.last_picture_filename)
            except Exception, e:
                print 'Send Failed ::', e
                self.status("Send failed :(")
                retcode = False
            self.status("")
        else:
            print 'Not signed in'
            retcode = False
        return retcode
    def __log_email_address(self,mail_address,consent_to_log,success,last_picture_filename):
        import time
        import datetime
        ts = datetime.datetime.fromtimestamp(time.time()).strftime("[%Y-%m-%d %H:%M]")
        sendcode = "?"
        if not consent_to_log:
            #user does'nt want his address to be logged
            mail_address = "xxx@xxx"
            if success:
                sendcode = '-'
            else:
                sendcode = "X"
        else:
            if success:
                sendcode = '*'
            else:
                sendcode = 'X'
        
        sendmail_log = open(EMAILS_LOG_FILE,"a")
        status = "%s (%s) %s %s\n"%(ts,sendcode,mail_address,os.path.basename(last_picture_filename))
        sendmail_log.write(status)
        sendmail_log.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-de", "--disable-email", help="disable the 'send photo by email' feature",
                    action="store_true")
    parser.add_argument("-du", "--disable-upload", help="disable the 'auto-upload to Google Photo' feature",
                    action="store_true")
    parser.add_argument("-df", "--disable-full-screen", help="disable the full-screen mode",
                    action="store_true")
    parser.add_argument("-dh", "--disable-hardware-buttons", help="disable the hardware buttons (on-screen buttons instead)",
                    action="store_true")
    args = parser.parse_args()
    
    #print args
    import configuration
    config = configuration.Configuration("configuration.json")
    if not config.is_valid:
        print "No configuration file found, please run setup.sh script to create one"
        sys.exit()
    
    # command line arguments have higher precedence than config
    if args.disable_upload and config.enable_upload:
        print "* Command line argument '--disable-upload' takes precedence over configuration"
        config.enable_upload = False

    if args.disable_email and config.enable_email:
        print "* Command line argument '--disable-email' takes precedence over configuration"
        config.enable_email = False

    if args.disable_hardware_buttons and config.enable_hardware_buttons:
        print "* Command line argument '--disable-hardware-buttons' takes precedence over configuration"
        config.enable_hardware_buttons = False

    if args.disable_full_screen and config.full_screen:
        print "* Command line argument '--disable-full-screen' takes precedence over configuration"
        config.full_screen = False
        
        
    #TODO move every arguments into config file
    ui = UserInterface(config,window_size=(SCREEN_W, SCREEN_H)) 

    ui.start_ui()




