# -*- coding: utf-8 -*-
"""
New interface for the photobooth

@author: Laurent Alacoque 2o18
"""

from Tkinter import *
import tkMessageBox
from PIL import ImageTk,Image
from tkkb import Tkkb
from tkImageLabel import ImageLabel
from constants import *
import custom as custom

import os
from credentials import OAuth2Login
import config as google_credentials
import hardware_buttons as HWB

CONFIG_BUTTON_IMG = "ressources/ic_settings.png"
EMAIL_BUTTON_IMG = "ressources/ic_email.png"
HARDWARE_POLL_PERIOD = 100


class UserInterface():
    def __init__(self, window_size=None, poll_period=HARDWARE_POLL_PERIOD, config=custom):
        self.root = Tk()
        self.root.configure(background='black')
        self.config=config
        if window_size is not None:
            self.size=window_size
        else:
            self.size=(640,480)
        
        self.root.geometry('%dx%d+0+0'%(self.size[0],self.size[1]))

        #Configure Image holder
        self.image = ImageLabel(self.root, size=self.size)
        self.image.place(x=0, y=0, relwidth = 1, relheight=1)
        self.image.configure(background='black')

        #Create config button
        cfg_image = Image.open(CONFIG_BUTTON_IMG)
        w,h = cfg_image.size
        self.cfg_imagetk = ImageTk.PhotoImage(cfg_image)
        self.cfg_btn   = Button(self.root, image=self.cfg_imagetk, height=h, width=w, command=self.launch_config)
        self.cfg_btn.place(x=0, y=0)
        self.cfg_btn.configure(background = 'black')        
        
        #Create sendmail Button
        mail_image = Image.open(EMAIL_BUTTON_IMG)
        w,h = mail_image.size
        self.mail_imagetk = ImageTk.PhotoImage(mail_image)
        self.mail_btn  = Button(self.root,image = self.mail_imagetk, height=h, width=w, command=self.send_email )
        self.mail_btn.place(x=SCREEN_W-w-2, y=0)
        self.mail_btn.configure(background = 'black')
        
        #Create status line
        self.status_lbl = Label(self.root, text="", font=("Helvetica", 20))
        self.status_lbl.config(background='black', foreground='white')
        self.status_lbl.place(x=self.cfg_btn['width'], y=0)
        
        #State variables
        self.signed_in = False
        self.auth_after_id = None
        self.poll_period = poll_period
        self.poll_after_id = None
        
        self.tkkb = None
        self.email_addr = StringVar()
        
        #Google credentials
        self.credentials = google_credentials.Credential()
        self.buttons = HWB.Buttons()
    
    def __del__(self):
        try:
            self.root.after_cancel(self.auth_after_id)
            self.root.after_cancel(self.poll_after_id)
        except:
            pass
        
    def status(self, status_text):
        self.status_lbl['text'] = status_text
    
    def start_ui(self):
        self.auth_after_id = self.root.after(100, self.refresh_auth)
        self.poll_after_id = self.root.after(self.poll_period, self.run_periodically)
        print "Done"
        self.root.mainloop()

        
    def launch_config(self):
        self.config.customize(self.root)
      
    
    def send_mail(self):
        self.send_email()
        
    def run_periodically(self):
        #do something here
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
        # when we snap, we should diable the polling
        self.root.after_cancel(self.poll_after_id)

        #do something here
        print "snap (mode=%s)" % mode

        # reenable the polling at the end
        self.poll_after_id = self.root.after(self.poll_period, self.run_periodically)

        
    def refresh_auth(self):
        if self.__google_auth():
            self.mail_btn.configure(state=NORMAL)
            self.signed_in = True
        else:
            self.mail_btn.configure(state=DISABLED)
            self.signed_in = False
            print 'refresh failed'

        #relaunch periodically
        self.auth_after_id = self.root.after(self.config.oauth2_refresh_period, self.refresh_auth)
        
    def __google_auth(self):
        # Connection to Google for Photo album upload
        try:
            # Create a client class which will make HTTP requests with Google Docs server.
            self.configdir = os.path.expanduser('./')
            self.client_secrets = os.path.join(self.configdir, 'OpenSelfie.json')
            self.credential_store = os.path.join(self.configdir, 'credentials.dat')
            self.client = OAuth2Login(self.client_secrets, self.credential_store, self.credentials.key)
            return True
        except Exception, e:
            print 'could not login to Google, check .credential file\n   %s' % e
            return False
        
    def send_email(self):
        if self.signed_in and self.tkkb is None:
            self.email_addr.set("")
            self.tkkb = Toplevel(self.root)
            def onEnter(*args):
                self.kill_tkkb()
                self.__send_picture()
            Tkkb(self.tkkb, self.email_addr, onEnter=onEnter)
            self.tkkb.wm_attributes("-topmost", 1)
            self.tkkb.transient(self.root)
            self.tkkb.protocol("WM_DELETE_WINDOW", self.kill_tkkb)
    def kill_tkkb(self):
        if self.tkkb is not None:
            self.tkkb.destroy()
            self.tkkb = None
            
    def __send_picture(self):
        email = self.email_addr.get()
        print "picture sent to %s"% _email

if __name__ == '__main__':
    ui = UserInterface(window_size=(SCREEN_W, SCREEN_H))
    ui.start_ui()




