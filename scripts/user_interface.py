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
import mailfile

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


class UserInterface():
    def __init__(self, config, window_size=None, poll_period=HARDWARE_POLL_PERIOD,  fullscreen = True, upload_images = True, send_emails = True,  hardware_buttons = True):
        self.root = Tk()
        if fullscreen:
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
        
        #Google credentials

        self.configdir = os.path.expanduser('./')
        self.oauth2service = oauth2services.OAuthServices(
            os.path.join(self.configdir, 'OpenSelfie.json'),
            os.path.join(self.configdir, 'credentials.dat'),
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
            X = 0
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
                btn.place(x=X,y=Y)
                btn.configure(background = 'black')
                X = X + w + padding
        
        #Camera
        self.camera = mycamera.PiCamera()
        self.camera.annotate_text_size = 160 # Maximum size
        self.camera.annotate_foreground = Color('white')
        self.camera.annotate_background = Color('black')
        
    
    def __del__(self):
        try:
            self.root.after_cancel(self.auth_after_id)
            self.root.after_cancel(self.poll_after_id)
            self.camera.close()
        except:
            pass
        
    def status(self, status_text):
        self.status_lbl['text'] = status_text
        self.root.update()
    
    def start_ui(self):
        self.auth_after_id = self.root.after(100, self.refresh_auth)
        self.poll_after_id = self.root.after(self.poll_period, self.run_periodically)
        self.root.mainloop()

        
    def run_periodically(self):
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
                        command = (['mv', self.last_picture_filename, new_filename])
                        subprocess.call(command)
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

    def refresh_auth(self):
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
        if not self.upload_images:
            return
        #upload to picasa album
        if caption is None:
            caption = config.photoCaption
        if config.albumID == 'None':
            config.albumID = None
        
        self.oauth2service.upload_picture(filen, config.albumID, title, caption)
        
            
    def send_email(self):
        if not self.send_emails:
            return
        self.suspend_poll = True
        if self.signed_in and self.tkkb is None:
            self.email_addr.set("")
            self.tkkb = Toplevel(self.root)
            def onEnter(*args):
                print "sending email..."+self.email_addr.get()
                self.kill_tkkb()
                self.__send_picture()
            #Tkkb(self.tkkb, self.email_addr, onEnter=onEnter)
            TouchKeyboard(self.tkkb,self.email_addr, onEnter = onEnter)
            self.tkkb.wm_attributes("-topmost", 1)
            self.tkkb.transient(self.root)
            self.tkkb.protocol("WM_DELETE_WINDOW", self.kill_tkkb)
            
    def kill_tkkb(self):
        if self.tkkb is not None:
            self.tkkb.destroy()
            self.tkkb = None
            self.suspend_poll = False
            
    def __send_picture(self):
        if not self.send_emails:
            return
        if self.signed_in:
            print 'sending photo by email to %s' % self.email_addr.get()
            self.status("Sending Email")
            try:
                self.oauth2service.send_email(
                    self.email_addr.get().strip(),
                    config.emailSubject,
                    config.emailMsg,
                    self.last_picture_filename)
                self.kill_tkkb()
            except Exception, e:
                print 'Send Failed ::', e
                self.status("Send failed :(")
            self.status("")
        else:
            print 'Not signed in'

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
        
        
    #TODO move every arguments into config file
    ui = UserInterface(config,window_size=(SCREEN_W, SCREEN_H), 
        fullscreen         = not args.disable_full_screen, 
        upload_images      = not args.disable_upload, 
        send_emails        = not args.disable_email, 
        hardware_buttons   = not args.disable_hardware_buttons)
    ui.start_ui()




