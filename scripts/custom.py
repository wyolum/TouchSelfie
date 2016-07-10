import listalbums
import Tkinter
import tkFileDialog
import tkSimpleDialog
import os.path
import Image
import ImageTk
import ConfigParser
import os.path
from constants import SCREEN_W, SCREEN_H

install_dir = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],  '..'))
conf_filename = os.path.join(install_dir, 'scripts', 'openselfie.conf')

def restore_conf():
    global emailSubject, emailMsg, photoCaption, logopng, albumID, countdown1, countdown2
    global TIMELAPSE, SIGN_ME_IN, ARCHIVE, archive_dir, logo, lxsize, lysize, oauth2_refresh_period

    if not os.path.exists(conf_filename):
        conf_file = open(conf_filename, 'w')
        default_conf = '''[main]
emailsubject = Your Postcard from the Wyolum Photobooth
emailmsg = Here's your picture from the http://wyolum.com photobooth!
photocaption = postcard from the xxx event
logopng = logo.png

albumid = None
countdown1 = 5
countdown2 = 3
timelapse = 0
sign_me_in = True
archive = True
archive_dir = %s/Photos/
oauth2_refresh_period = 1800000
''' % install_dir
        conf_file.write(default_conf)
        conf_file.close()
    if not os.path.exists(conf_filename):
        raise ValueError('Configuration file "%s" is missing.' % conf_filename)

    conf = ConfigParser.ConfigParser()
    conf.read(conf_filename)

    emailSubject = conf.get('main', 'emailSubject') # "Your Postcard from the Wyolum Photobooth"
    emailMsg = conf.get('main', 'emailMsg') # "Here's your picture from the http://wyolum.com photobooth!"
    logopng = conf.get('main', 'logopng') # "logo.png"

    if os.path.exists(logopng):
        logo = Image.open(logopng)
        lxsize, lysize = logo.size
    else:
        logo = None
        lxsize = 0
        lysize = 0

    photoCaption = conf.get('main', 'photoCaption') # "postcard from the xxxx event"
    albumID = conf.get('main', 'albumID') # None ### Put your own album ID here in single quotes like '5991903863088919889'

    countdown1 = int(conf.get('main', 'countdown1')) # 5 ## how many seconds to count down before a photo is taken
    countdown2 = int(conf.get('main', 'countdown2')) # 3 ## how many seconds to count down before subsequent photos are taken

    TIMELAPSE = float(conf.get('main', 'TIMELAPSE')) # 0 ## use 0 for no time lapse photos, at least 3 (seconds)
    SIGN_ME_IN = conf.get('main', 'SIGN_ME_IN')
    if SIGN_ME_IN == "True":
        SIGN_ME_IN = True
    else:
        SIGN_ME_IN = False
    ARCHIVE = bool(conf.get('main', 'ARCHIVE')) # True ## archive photos?
    archive_dir = conf.get('main', 'archive_dir') # './'
    oauth2_refresh_period = int(conf.get('main', 'oauth2_refresh_period')) # 1800000

restore_conf()

### set up GUI
BUTTON_FONT = ('Times', 24)
CANVAS_FONT = ("times", 50)

## usually not need to change these.
EXT = 'jpg'     
RAW_FILENAME = 'image.' + EXT
PROC_FILENAME = 'photo.' + EXT

class AskBoolean(tkSimpleDialog.Dialog):
    def apply(self):
        self.result = True

class curry:
    def __init__(self, callable, *args):
        self.callable = callable
        self.args = args
    
    def __call__(self, *args):
        return self.callable(*self.args)

def ispi():
    return os.path.exists('/dev/ttyS0')

logo_label = None
def display_logo(parent, logopng):
    global logo_label
    if ispi():
        photo = Image.open(logopng)
        width, height = photo.size
        if SCREEN_W / width < SCREEN_H / height:
            scale = (.25 * SCREEN_W) / width
        else:
            scale = (.25 * SCREEN_H) / height
        photo = photo.resize((int(width * scale), int(height * scale)))
        photo_tk = ImageTk.PhotoImage(photo) 
    else:
        photo_tk = Tkinter.PhotoImage(file=logopng) ## works but not on raspberry pi
    try: ## subsequent calls only need config
        logo_label.config(image=photo_tk)
        logo_label.photo_tk = photo_tk
    except: ## initial call creates a new label
        logo_label = Tkinter.Label(parent, image=photo_tk)
        logo_label.photo_tk = photo_tk
        logo_label.pack(side=Tkinter.LEFT)

def customize(master):
    global logo_label
    self = Tkinter.Toplevel(master)
    self.master = master
    def close_master():
        self.master.destroy()
    def string_customizer(label, initial_val, listener):
        label = ' ' * (20 - len(label)) + label
        frame = Tkinter.Frame(self)
        var = Tkinter.StringVar()
        var.set(initial_val)
        Tkinter.Label(frame, text=label).pack(side=Tkinter.LEFT)
        entry = Tkinter.Entry(frame, textvariable=var, width=60)
        var.trace('w', lambda *args:listener(var, entry))
        entry.pack(side=Tkinter.RIGHT)
        frame.pack()
        return frame, entry
    
    def bool_customizer(label, initial_val, listener):
        frame = Tkinter.Frame(self)
        var = Tkinter.BooleanVar()
        var.set(initial_val)
        checkbox = Tkinter.Checkbutton(self, text=label, variable=var)
        var.trace('w', lambda *args:listener(var, checkbox))
        checkbox.pack()
        frame.pack()

    def update_subj(var, wid):
        global emailSubject
        emailSubject = var.get()

    def update_msg(var, wid):
        global emailMsg
        emailMsg = var.get()
        
    def update_caption(var, wid):
        global photoCaption
        photoCaption = var.get()

    def update_albumID(var, wid):
        global albumID
        albumID = var.get()
        
    def update_countdown1(var, wid):
        global countdown1
        try:
            wid.config(bg='white')
            countdown1 = int(var.get())
        except:
            wid.config(bg='red')
            pass

    def update_countdown2(var, wid):
        global countdown2
        try:
            wid.config(bg='white')
            countdown2 = int(var.get())
        except:
            wid.config(bg='red')
            pass

    def update_timelapse(var, wid):
        global TIMELAPSE
        try:
            wid.config(bg='white')
            TIMELAPSE = float(var.get())
        except:
            wid.config(bg='red')
    def update_sign_me_in(var, wid):
        global SIGN_ME_IN
        wid.config(bg='white')
        
        SIGN_ME_IN = var.get()
        
    def update_archive(var):
        global ARCHIVE, archive_dir
        archive_dir = var.get()
        if os.path.exists(archive_dir):
            ARCHIVE = True
        else:
            ARCHIVE = False
        
    def update_logo(entry):
        if os.path.exists(logo_var.get()):
            entry.config(bg='white')
            logopng = logo_var.get()
            if True: ## DISPLAY_LOGO 
                display_logo(self, logopng)
        else:
            entry.config(bg='red')
            logopng = 'None'

    def update_and_close(*argss):
        global logo,logo_label, lxsize, lysize
        if os.path.exists(logopng):
            logo = Image.open(logopng)
            lxsize, lysize = logo.size
        else:
            logo = None
            lxsize = 0l
            lysize = 0

        ## save popup dialog
        # save_dialog = AskBoolean(self, title='Save configuration?')
        # if save_dialog.result:
        if True:
            conf = ConfigParser.ConfigParser()
            conf.add_section('main')
            conf.set('main', 'emailSubject', emailSubject)
            conf.set('main', 'emailMsg', emailMsg)
            conf.set('main', 'photoCaption', photoCaption)
            conf.set('main', 'logopng', logopng)
            conf.set('main', 'albumID', albumID)
            conf.set('main', 'countdown1', countdown1)
            conf.set('main', 'countdown2', countdown2)
            conf.set('main', 'TIMELAPSE', TIMELAPSE)
            conf.set('main', 'SIGN_ME_IN', SIGN_ME_IN)
            conf.set('main', 'ARCHIVE', ARCHIVE)
            conf.set('main', 'archive_dir', archive_dir)
            conf.set('main', 'oauth2_refresh_period', oauth2_refresh_period)
            f = open(conf_filename, 'w')
            conf.write(f)
            print 'wrote', f.name
        else:
            restore_conf()
        close()
    def close():
        self.destroy()

    def logo_dialog():
        global logopng
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('Images', '.png'), ('all files', '.*')]
        options['initialdir'] = './'
        options['initialfile'] = logo_var.get()
        options['title'] = 'Logo finder'
        options['parent'] = self
        logo_file = tkFileDialog.askopenfilename(**options)
        logo_var.set(logo_file)
        logopng = logo_file

    def archive_dialog():
        options = {}
        options['initialdir'] = '/media'
        options['title'] = 'Select Archive Directory'
        options['parent'] = self
        archive_dir = tkFileDialog.askdirectory(**options)
        archive_var.set(archive_dir)
    def launch_album_select(*args):
        if not hasattr(self, 'albums'):
            self.albums = listalbums.getAlbums("kevin.osborn@gmail.com")
        listalbums.AlbumSelect(self, self.album_entry, self.albums)
        
    string_customizer('Email Subject', emailSubject, update_subj)
    string_customizer('Email Msg', emailMsg, update_msg)
    string_customizer('Caption', photoCaption, update_caption)
    album_frame, self.album_entry = string_customizer('albumID',
                                                      albumID,
                                                      update_albumID)
    ### add in Album selector
    Tkinter.Button(album_frame,
                   text="Lookup",
                   command=launch_album_select).pack()
    
    string_customizer('Countdown1', countdown1, update_countdown1)
    string_customizer('Countdown2', countdown2, update_countdown2)
    string_customizer('Timelapse', TIMELAPSE, update_timelapse)
    bool_customizer('Sign me in', SIGN_ME_IN, update_sign_me_in)
    archive_var = Tkinter.StringVar()
    archive_var.set(archive_dir)
    archive_frame = Tkinter.Frame(self)
    Tkinter.Label(archive_frame, text='Archive Directory').pack(side=Tkinter.LEFT)
    archive_entry = Tkinter.Entry(archive_frame, textvariable=archive_var, width=60)
    archive_entry.pack(side=Tkinter.LEFT)
    archive_var.trace('w', curry(update_archive, archive_entry))
    Tkinter.Button(archive_frame, text='Browse', command=archive_dialog).pack(side=Tkinter.LEFT)
    archive_frame.pack(side=Tkinter.TOP)

    logo_var = Tkinter.StringVar()
    logo_var.set(logopng)
    logo_frame = Tkinter.Frame(self)
    Tkinter.Label(logo_frame, text='Logo File').pack(side=Tkinter.LEFT)
    logo_entry = Tkinter.Entry(logo_frame, textvariable=logo_var, width=60)
    logo_entry.pack(side=Tkinter.LEFT)
    logo_var.trace('w', curry(update_logo, logo_entry))
    Tkinter.Button(logo_frame, text='Browse', command=logo_dialog).pack(side=Tkinter.LEFT)
    logo_frame.pack(side=Tkinter.TOP)
    buttonbox = Tkinter.Frame(self)
    ##  Tkinter.Button(buttonbox, text='Cancel', command=self.destroy).pack(side=Tkinter.LEFT) changes are stored when they are made. cancel is harder than this
    Tkinter.Button(buttonbox, text='Save', command=update_and_close).pack(
        side=Tkinter.LEFT)
    Tkinter.Button(buttonbox, text='Cancel', command=close).pack(
        side=Tkinter.LEFT)
    Tkinter.Button(buttonbox, text='Quit TouchSelfie', command=quit).pack(
        side=Tkinter.LEFT)
    buttonbox.pack()
    
    if True: # DISPLAY_LOGO:
        display_logo(self, logopng)

if __name__ == '__main__':
    import Tkinter
    r = Tkinter.Tk()
    b = Tkinter.Button(r, text='help', command=lambda :customize(r))
    b.pack()
    r.mainloop()
    print emailSubject
    print emailMsg
    print photoCaption
    print countdown1
    print countdown2
    print TIMELAPSE
    print ARCHIVE
    print archive_dir
    print logopng
    



    
