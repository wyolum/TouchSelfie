import json
import os

class Configuration():
    # default values
    user_name = None
    logo_file = None
    countdown1  = 5 # seconds of preview before first snap
    countdown2  = 3 # seconds of preview between snaps (Four pictures mode)
    photoCaption = "" # Caption in the photo album
    ARCHIVE      = True # Do we archive photos locally
    archive_dir  = os.path.join("..","Photos") # Where do we archive photos
    albumID      = None #  use install_credentials.py to create 'album.id'
    emailSubject = "Here's your photo!" # subject line of the email sent from the photobooth
    emailMsg     = "Greetings, here's your photo sent from the photobooth" # Brief body of the message sent from the photobooth
    #init
    def __init__(self,configuration_file_name):
        self.config_file = configuration_file_name
        self.is_valid = False
        self.__read_config_file()
    
    def __read_config_file(self):
        self.is_valid = True
        try:
            with open(self.config_file, 'r') as content_file:
                file_content = content_file.read()
            config = json.loads(file_content)
        except Exception as error:
            print "Error while parsing %s config file : %s"%(self.config_file,error)
            self.is_valid = False
            return False
        if "gmail_user" in config.keys():  self.user_name = config['gmail_user']
        else:
            #mandatory configuration!!
            self.is_valid = False


        # all other configuration keys are optional
        if "countdown_before_snap" in config.keys(): self.countdown1 = config["countdown_before_snap"]
        if "countdown_inter_snap" in config.keys():  self.countdown2 = config["countdown_inter_snap"]
        if "snap_caption" in config.keys():  self.photoCaption = config["snap_caption"]
        if "local_archive" in config.keys():  self.ARCHIVE = config["local_archive"]
        if "local_archive_dir" in config.keys():  self.archive_dir = config["local_archive_dir"]
        if "google_photo_album_id" in config.keys():  self.albumID = config["google_photo_album_id"]
        if "email_subject" in config.keys():  self.emailSubject = config["email_subject"]
        if "email_body" in config.keys():  self.emailMsg = config["email_body"]
        if "logo_file" in config.keys():  self.logo_file = config["logo_file"]
        return self.is_valid
    
    
    def write_default_config(self,user_name):
        myconfig = {
            "gmail_user": user_name,
            "countdown_before_snap": self.countdown1,
            "countdown_inter_snap": self.countdown2,
            "snap_caption": self.photoCaption,
            "local_archive" : self.ARCHIVE,
            "local_archive_dir" : self.archive_dir,
            "google_photo_album_id" : self.albumID,
            "email_subject": self.emailSubject,
            "email_body":self.emailMsg,
            "logo_file": self.logo_file
        }
        try:
            with open(self.config_file,'w') as config:
                config.write(json.dumps(myconfig, indent =4, sort_keys=True))
        except Exception as error:
            raise ValueError("Problem writing %s configuration file: %s"%(self.config_file,error))
            
            
if __name__ == "__main__":

    config = Configuration("myconf.conf")
    if not config.is_valid:
        config.write_default_config("user@gmail.com")