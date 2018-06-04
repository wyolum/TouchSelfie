# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 09:31:58 2018

@author: LA203179
"""

from Tkinter import *
import tkMessageBox
from PIL import ImageTk,Image
from tkkb import Tkkb
from tkImageLabel import ImageLabel
from constants import *
import custom as custom

CONFIG_BUTTON_IMG = "ic_settings.png"
EMAIL_BUTTON_IMG = "ic_email.png"
HARDWARE_POLL_PERIOD = 1000


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
        self.image.load('photo.jpg')
      
    
    def send_mail(self):
        self.send_email()
        
    def run_periodically(self):
        #do something here
        print "Polling"
        self.status('')
        self.poll_after_id = self.root.after(self.poll_period, self.run_periodically)

        
    def refresh_auth(self):
        # toggle state (test)
        self.signed_in = not self.signed_in
        if self.signed_in:
            self.mail_btn.configure(state=NORMAL)
        else:
            self.mail_btn.configure(state=DISABLED)
        #relaunch periodically
        #self.auth_after_id = self.root.after(custom.oauth2_refresh_period, self.refresh_auth)
        print "Auth refresh"
        self.status('poll: '+self.poll_after_id)
        self.auth_after_id = self.root.after(5000, self.refresh_auth)
    
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
        _email = self.email_addr.get()
        print "picture sent to %s"% _email

if __name__ == '__main__':
    ui = UserInterface(window_size=(SCREEN_W, SCREEN_H))
    ui.image.load('anim.gif')
    ui.start_ui()




