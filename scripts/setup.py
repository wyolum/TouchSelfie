"""
    Graphical and Command-line setup scripts for TouchSelfie

    This script is an assistant that guides users
    through the process of configuring wanted features
    and optionally
        - creating a Google Project to allow OAuth2 authentication
        - creating the configuration.json file
        - creating the startup script photobooth.sh
"""
import os.path
import sys
import configuration
import constants
import mykb
try:
    import cups
    printer_selection_enable = True
except ImportError:
    print("Cups not installed. removing option")
    printer_selection_enable = False

VALID_ICON_FILE = os.path.join("ressources","ic_valid.png")
INVALID_ICON_FILE = os.path.join("ressources","ic_invalid.png")
from PIL import Image as _Image
from PIL import ImageTk as _ImageTk
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import oauth2services

#URL of the Google console developer assistant to create App_id file
GET_APP_ID_WIZARD_URL="https://console.developers.google.com/start/api?id=gmail"

class Assistant(Tk):
    """A page-by-page assistant based on Tk"""
    BUTTONS_BG = '#4285f4'
    BUTTONS_BG_INACTIVE = 'white'
    BUTTONS_BG_ACTION = '#db4437'
    USE_SOFT_KEYBOARD = True
    def __init__(self,config,*args,**kwargs):
        """This creates all the widgets and variables"""
        Tk.__init__(self,*args,**kwargs)
        try:
            self.google_service = None
            self.printer_selection_enable = printer_selection_enable
            self.config( bg = "white")
            self.config = config
            self.packed_widgets = []
            self.page = 0
            self.main_frame = Frame(self, bg = "white")
            self.buttons_frame = Frame(self, bg='white')
            self.b_next = Button(self.buttons_frame,text="Next", fg='white', bg=self.BUTTONS_BG,width=10, command=self.__increment, font='Helvetica')
            self.b_prev = Button(self.buttons_frame,text="Prev", fg='white', bg=self.BUTTONS_BG, width=10, command=self.__decrement, font='Helvetica')
            self.main_frame.pack(fill=X,ipadx=10,ipady=10)
            self.buttons_frame.pack(side=BOTTOM)
            self.b_prev.pack(side=LEFT,padx=40)
            self.b_next.pack(side=RIGHT,padx=40)
            self.widgets=[]

            #variables
            #PAGE 0 email/upload
            self.want_email_var = IntVar()
            self.want_email_var.set(config.enable_email == True)
            def on_want_email_change(*args):
                self.config.enable_email = self.want_email_var.get() != 0
            self.want_email_var.trace("w",on_want_email_change)

            self.want_upload_var = IntVar()
            self.want_upload_var.set(config.enable_upload == True)
            def on_want_upload_change(*args):
                self.config.enable_upload = self.want_upload_var.get() != 0
            self.want_upload_var.trace("w",on_want_upload_change)

            self.want_effects_var = IntVar()
            self.want_effects_var.set(config.enable_effects == True)
            def on_want_effects_change(*args):
                self.config.enable_effects = self.want_effects_var.get() != 0
            self.want_effects_var.trace("w",on_want_effects_change)

            if self.printer_selection_enable == True:
                self.want_print_var = IntVar()
                self.want_print_var.set(config.enable_print == True)
                def on_want_print_change(*args):
                    self.config.enable_print = self.want_print_var.get() !=0
                    if self.config.enable_print == True:
                        try:
                            self.use_print_list = Listbox(self.main_frame)
                            self.use_print_list.bind('<<ListboxSelect>>', on_use_printer)
                            #self.use_print_list.pack()
                            self.__erase_page()
                            self.widgets.pop(0)
                            self.widgets.insert(0,[self.want_email_cb, self.want_upload_cb, self.want_effects_cb, self.want_print_cb, self.use_soft_keyboard_cb,self.use_print_list])

                            conn = cups.Connection()
                            printers = conn.getPrinters()

                            for printer in printers:
                                #print printer, printers[printer]["device-uri"]
                                self.use_print_list.insert(END, printer)
                            self.__draw_page()
                        except:
                            tkinter.messagebox.showerror("Missing Driver","""You need CUPS installed and a printer setup. Please look in the Readme file for a link on how to setup CUPS on your system. The printer option will be disabled for this setup.""")
                            self.__erase_page()
                            self.widgets.pop(0)
                            self.widgets.insert(0,[self.want_email_cb, self.want_upload_cb,self.want_effects_cb, self.use_soft_keyboard_cb])
                            self.__draw_page()
                            self.enable_print = False;
                            self.config.enable_print = False; #Fix printing enabled even on error
                            self.selected_printer = None;






            if printer_selection_enable == True:self.want_print_var.trace("w",on_want_print_change)

            self.want_email_cb  = Checkbutton(self.main_frame, text="Enable Email sending", variable=self.want_email_var, anchor=W, font='Helvetica')
            self.want_upload_cb  = Checkbutton(self.main_frame, text="Enable photo upload", variable=self.want_upload_var, anchor=W, font='Helvetica')
            self.want_effects_cb  = Checkbutton(self.main_frame, text="Enable image effects", variable=self.want_effects_var, anchor=W, font='Helvetica')

            if printer_selection_enable == True:
                self.want_print_cb = Checkbutton(self.main_frame, text="Enable photo print", variable=self.want_print_var, anchor=W, font='Helvetica')
                self.want_printer_val = int()

            #self.want_printer_val.set(config.selected_printer)
            def on_use_printer(evt):
                printer_selected = evt.widget
                self.want_printer_val = int(printer_selected.curselection()[0])
                self.config.selected_printer = int(self.want_printer_val)
                #value = self.want_printer_val.get(index)
                print('You selected item %d: ' % (self.want_printer_val))


            #checkbutton to choose to use soft keyboard

            self.use_soft_keyboard_var = IntVar()
            def on_use_soft_keyboard(*args):
                self.USE_SOFT_KEYBOARD = self.use_soft_keyboard_var.get() != 0
            self.use_soft_keyboard_var.trace("w",on_use_soft_keyboard)
            self.use_soft_keyboard_var.set(0)

            self.use_soft_keyboard_cb = Checkbutton(self.main_frame, text="Enable software keyboard (for this configuration)", variable=self.use_soft_keyboard_var, anchor=W, font='Helvetica')
            if self.printer_selection_enable == True:
                self.widgets.append([self.want_email_cb, self.want_upload_cb, self.want_effects_cb,self.want_print_cb,self.use_soft_keyboard_cb])
            else:
                self.widgets.append([self.want_email_cb, self.want_upload_cb,self.want_effects_cb,self.use_soft_keyboard_cb])

            #PAGE 1 google credentials
            self.user_mail_label = Label(self.main_frame,text="Google Account", font='Helvetica', anchor=W)
            self.user_mail_var  = StringVar()
            def on_mail_change(*args):
                self.config.user_name = self.user_mail_var.get()

            self.user_mail_var.trace("w",on_mail_change)
            self.user_mail_var.set(config.user_name)
            self.user_mail_entry =  Entry(self.main_frame, font='Helvetica', textvariable = self.user_mail_var)
            self.__install_soft_keyboard(self.user_mail_entry, self.user_mail_var)

            #load valid/invalid icons
            valid_icon = _Image.open(VALID_ICON_FILE)
            self.valid_icon = _ImageTk.PhotoImage(valid_icon)
            invalid_icon = _Image.open(INVALID_ICON_FILE)
            self.invalid_icon = _ImageTk.PhotoImage(invalid_icon)

            self.credentials_frame = LabelFrame(self.main_frame, text="Credentials", font='Helvetica')
            self.__check_credentials_files()

            self.refresh_cred_button = Button(self.main_frame, text="Refresh", font='Helvetica', fg=self.BUTTONS_BG, command=self.__check_credentials_files)


            self.widgets.append([
                self.user_mail_label,
                self.user_mail_entry,
                self.credentials_frame,
                self.refresh_cred_button])

            #PAGE 2 Email infos

            self.email_title_var = StringVar()
            self.email_title_var.set(config.emailSubject)
            def on_mail_title_change(*args):
                self.config.emailSubject = self.email_title_var.get()
            self.email_title_var.trace("w",on_mail_title_change)

            self.email_body_var = StringVar()
            self.email_body_var.set(config.emailMsg)
            def on_mail_body_change(*args):
                self.config.emailMsg = self.email_body_var.get()
            self.email_body_var.trace("w",on_mail_body_change)

            self.email_title_label = Label(self.main_frame,text="Email subject:", font='Helvetica', anchor=W)
            self.email_title_entry = Entry(self.main_frame, textvariable=self.email_title_var, font='Helvetica', width = 40)
            self.__install_soft_keyboard(self.email_title_entry, self.email_title_var)

            self.email_body_label = Label(self.main_frame,text="Email body:", font='Helvetica', anchor=W)
            #self.email_body_entry = Entry(self.main_frame, textvariable=self.email_body_var, width = 40)
            self.email_body_entry =  Text(self.main_frame, font='Helvetica', height=5)
            self.email_body_entry.insert(INSERT,self.email_body_var.get())
            self.__install_soft_keyboard(self.email_body_entry,self.email_body_var)

            self.email_logging_var = IntVar()
            if self.config.enable_email_logging: self.email_logging_var.set(1)
            else : self.email_logging_var.set(0)
            def on_email_logging_change(*args):
                self.config.enable_email_logging = self.email_logging_var.get() != 0
            self.email_logging_var.trace("w",on_email_logging_change)
            self.email_logging_cb = Checkbutton(self.main_frame, text="Log email addresses?", variable=self.email_logging_var, anchor=W, font='Helvetica')


            def test_email():
                self.__mail_body_update_content()
                self.__test_connection(True,False)

            self.test_email_button = Button(self.main_frame,text="Send test email", font='Helvetica', command=test_email)

            self.widgets.append([
                self.email_title_label,
                self.email_title_entry,
                self.email_body_label,
                self.email_body_entry,
                self.email_logging_cb,
                self.test_email_button])

            #PAGE 3 Album ID

            self.album_name_label = Label(self.main_frame,text="Google Photo Album:", font='Helvetica', anchor=W)

            self.album_name_var = StringVar()
            def on_album_name_change(*args):
                self.config.album_name = self.album_name_var.get()
            self.album_name_var.trace("w",on_album_name_change)
            self.album_name_var.set(config.album_name) #TODO restore this eventually
            #self.album_name_var.set("Photo Stream")

            self.album_id_var = StringVar()
            def on_albumID_change(*args):
                album_id = self.album_id_var.get()
                album_id = album_id.strip()
                if album_id == "":
                    self.config.albumID=None
                else:
                    #print("ERROR it's currently impossible to send photos to a specific album")
                    self.config.albumID = self.album_id_var.get()
                    #self.config.albumID = None # TODO: find a way to upload in a specific album
            self.album_id_var.trace("w",on_albumID_change)
            
            self.album_id_var.set(config.albumID) #TODO: restore this eventually
            #self.album_id_var.set(None) # No Album

            self.album_id_label = Label(self.main_frame,text="Album ID", font='Helvetica', anchor=W)
            self.album_name_entry = Entry(self.main_frame,textvariable=self.album_name_var, font='Helvetica', state=DISABLED, disabledbackground="#eeeeee", disabledforeground="#222222")
            self.album_name_entry.config(fg="black",bg="#eeeeee")
            self.album_id_entry = Entry(self.main_frame,textvariable = self.album_id_var, font='Helvetica', state=DISABLED)

            def select_album():
                """Popup control to select albums"""
                print("Album selection")
                connected=False
                try:
                    connected = self.google_service.refresh()
                except:
                    pass
                if not connected:
                    print("Error: impossible to connect to Google\n")
                    return
                #Create an album selection control
                top = Toplevel(self,bg='white')
                top.geometry("450x400")
                loading_lbl = Label(top,text="Loading album list...", bg='white', font='Helvetica')
                loading_lbl.pack(fill=X)
                top.update()
                album_list = self.google_service.get_user_albums()
                
                        
                loading_lbl.config(text='Use field below to search\nDouble-click on the list to apply')
                #entry and listbox
                pattern_var = StringVar()
                pattern_entry = Entry(top,font='Helvetica',textvariable=pattern_var)
                self.__install_soft_keyboard(pattern_entry, pattern_var)

                pattern_entry.pack(fill=X)

                list_box_items = 15
                album_listbox = Listbox(top,height=list_box_items, font='Helvetica', selectmode=SINGLE)
                album_listbox.pack(fill=X)

                displayed_list_ids=["idstart"]
                displayed_list_names=["namestart"]
                def populate_list(*args):
                    global displayed_list_ids, displayed_list_names
                    pattern = pattern_var.get()
                    #print "applying pattern %s"%pattern
                    #clear
                    displayed_list_ids = ["","<New>"]
                    displayed_list_names=["<No Album>","<Create New>"]
                    album_listbox.delete(0,END)
                    album_listbox.insert(END,"<No Album>")
                    album_listbox.insert(END,"<Create New>")
                    inserted_items = 0
                    for i, item in enumerate(album_list):
                        if inserted_items >= list_box_items-1:
                            break;
                        title = item['title']
                        title_ = title.lower()
                        id    = item['id']
                        if title_.find(pattern.lower()) != -1:
                            album_listbox.insert(END,item['title'])
                            displayed_list_ids.append(id)
                            displayed_list_names.append(title)
                            inserted_items += 1


                populate_list()
                pattern_var.trace("w",populate_list)
                def item_selected(*args):
                    global displayed_list_ids, displayed_list_names
                    #print "selected!"
                    cursel = album_listbox.curselection()
                    cursel = int(cursel[0])
                    #print cursel
                    #print displayed_list_ids
                    #print displayed_list_names
                    print("selected album '%s' with id '%s'"%(displayed_list_names[cursel],displayed_list_ids[cursel]))
                    if displayed_list_names[cursel] == "<Create New>":
                        try:
                            #No album found, create one
                            album_id = self.google_service.create_album(album_name = "TouchSelfie", add_placeholder_picture = True)
                            self.album_id_var.set(album_id)   
                            self.album_name_var.set("TouchSelfie")
                        except Exception as e:
                            print(e)
                    else:
                        self.album_id_var.set(displayed_list_ids[cursel])
                        self.album_name_var.set(displayed_list_names[cursel])
                    top.destroy()

                album_listbox.bind("<Double-Button-1>",item_selected)
                self.wait_window(top)




            #Select Album and test buttons
            self.album_bframe = Frame(self.main_frame, bg='white')

            self.album_select_button = Button(self.album_bframe,text='Select',fg='white',bg=self.BUTTONS_BG, command=select_album, font='Helvetica')
            self.album_select_button.pack(side=LEFT)

            



            def test_upload():
                self.__test_connection(False,True)

            self.upload_test_button = Button(self.album_bframe, text='Test Upload',fg='white',bg=self.BUTTONS_BG, command=test_upload, font='Helvetica')
            self.upload_test_button.pack(side=RIGHT)


            #self.widgets.append([self.album_name_label,self.current_album_label,self.album_name_entry,self.album_id_label, self.album_id_entry,self.album_bframe])
            self.widgets.append([self.album_name_label,self.album_name_entry,self.album_bframe])

            #PAGE 4 Archive
            self.archive_var = IntVar()
            if config.ARCHIVE: self.archive_var.set(1)
            else : self.archive_var.set(0)

            def on_archive_change(*args):
                self.config.ARCHIVE = self.archive_var.get() != 0
            self.archive_var.trace("w",on_archive_change)


            self.archive_dir_label = Label(self.main_frame,text="Local directory for archive:", font='Helvetica', anchor=W)
            self.archive_dir_var = StringVar()
            self.archive_dir_var.set(config.archive_dir)
            def on_archive_dir_change(*args):
                self.config.archive_dir = self.archive_dir_var.get()
            self.archive_dir_var.trace("w",on_archive_dir_change)

            self.archive_dir_entry = Entry(self.main_frame, textvariable=self.archive_dir_var, width = 40, font='Helvetica')
            self.__install_soft_keyboard(self.archive_dir_entry,self.archive_dir_var)
            def change_dir():
                directory = tkinter.filedialog.askdirectory(initialdir=self.archive_dir_var.get(), title="Choose directory for snapshots archive")
                self.archive_dir_var.set(directory)
                print("changed dir to %s"%directory)

            self.choose_archive_dir_button = Button(self.main_frame, text="Choose directory", fg='white',bg=self.BUTTONS_BG, font='Helvetica', command=change_dir)


            def enable_archive_dir():
                if self.archive_var.get() == 0:
                    self.archive_dir_entry.config(state = DISABLED)
                    self.choose_archive_dir_button.config(state = DISABLED, bg='white',fg='grey')
                else:
                    self.archive_dir_entry.config(state = NORMAL)
                    self.choose_archive_dir_button.config(state = NORMAL, bg=self.BUTTONS_BG,fg='white')

            self.archive_cb = Checkbutton(self.main_frame,text="Archive snapshots locally", variable = self.archive_var, command=enable_archive_dir, font='Helvetica', anchor=W)
            enable_archive_dir()
            self.widgets.append([
                self.archive_cb,
                self.archive_dir_label,
                self.archive_dir_entry,
                self.choose_archive_dir_button])

            for widget_page in self.widgets:
                for widget in widget_page:
                    if widget.winfo_class() == 'Button':
                        if widget['state'] != DISABLED:
                            widget.config(foreground='white',background=self.BUTTONS_BG)
                        else:
                            widget.config(foreground='grey',background=self.BUTTONS_BG_INACTIVE)
                    else:
                        widget.config(background='white')

            self.__draw_page()
        except:
            self.update()
            self.destroy()
            raise Exception("Error during interface creation")

    def __mail_body_update_content(self):
        self.email_body_var.set(self.email_body_entry.get('1.0','end'))
        #print "msg body: %s"%self.email_body_var.get()
        return self.email_body_var.get()

    def __remove_app_id(self):
        print("removing %s"%constants.APP_ID_FILE)
        self.__ask_for_removal(constants.APP_ID_FILE,"Are you sure you want to remove the App ID file?\nYou'll need to download it again from your developer's console.")

    def __remove_cred_store(self):
        print("removing %s"%constants.CREDENTIALS_STORE_FILE)
        self.__ask_for_removal(constants.CREDENTIALS_STORE_FILE,"Are you sure you want to remove the credentials storage file?\nYou'll need to authorize your application again.")

    def __install_soft_keyboard(self,entry,stringvar):
        """Bind a soft keyboard to the entry if needed"""
        def launch_keyboard(*args):
            if not self.USE_SOFT_KEYBOARD:
                return
            self.soft_keyboard = Toplevel(self)
            #Bind the keyboard output to the variable
            def kill_keyboard():
                """Kill the popup keyboard"""
                if self.soft_keyboard is not None:
                    self.soft_keyboard.destroy()
                    self.soft_keyboard = None
            def onEnter(*args):
                print("updating value")
                if entry.winfo_class() == 'Text':
                    #copy the content of stringvar that just got modified into the text
                    text_content = stringvar.get()
                    entry.delete('1.0',END)
                    entry.insert(END, text_content)
                kill_keyboard()

            mykb.TouchKeyboard(self.soft_keyboard, stringvar, onEnter = onEnter)
            self.soft_keyboard.wm_attributes("-topmost", 1)
            self.wait_window(self.soft_keyboard)
        #Bind the window click event to the entry
        entry.bind('<Button-1>',launch_keyboard)

    def __get_app_id(self):
        print("Getting App ID")
        message="""    ________________________________________________________________

    Photo upload or email sending requires that you create a
    Google Project and download the project's credentials to
    the scripts/ directory
    Note: you can do the following on any computer (except step 5/)
    ________________________________________________________________

    1/  Go to https://console.developers.google.com/start/api?id=gmail
    2/  Select "Create a project" and click continue
    3/  Follow the assistant with these hints:
        - Platform : other (with command-line user interface)
        - Access   : User data
        - <credentials> : Create an OAuth 2.0 client ID
        - Fill whatever your like for application name and ID name
    4/  The last step of the assistant makes you Download
        a json file : this is your project's credentials!
    5/  Copy the downloaded file to : scripts/%s
    6/  Next, on the console.developers.google.com website:
        - go to the "<Menu>/APIs and Services/Library"
        - search for "Photos"
        - click on the "Photos Library API" Card
        - click on the "Enable" Button

    see this page for up-to-date informations:
    https://support.google.com/googleapi/answer/6158849

"""%(constants.APP_ID_FILE)
        #Create a toplevel window with checkboxes and a "Quit application button"
        top = Toplevel(self)
        text_frame=Frame(top, bg='white')
        text_frame.pack(side=TOP,fill=X)


        def launch_browser():
            import webbrowser
            webbrowser.open(GET_APP_ID_WIZARD_URL)

        button_frame = Frame(top,bg='white')
        button_frame.pack(side=BOTTOM, fill=X)
        qb = Button(button_frame,text="Launch browser", font='Helvetica', fg="white", bg=self.BUTTONS_BG, command=launch_browser)
        qb.pack( side = LEFT,pady=20,padx=20)
        dismiss_button = Button(button_frame,text="Dismiss", font='Helvetica', fg="white", bg=self.BUTTONS_BG, command=top.destroy)
        dismiss_button.pack( side= RIGHT, pady=20,padx=20)

        message_box = Text(text_frame, font=('Helvetica',10), height=25)
        message_box.insert(INSERT,message)
        message_box.pack(fill=X)
        self.wait_window(top)

        #update displayed
        self.__check_credentials_files()

    def __connect_app(self):
        print("Connecting App")

        #Create a graphical handler for the authorization
        def auth_handler(URI):
            top = Toplevel(self, bg='white')
            text_frame=Frame(top, bg='white')
            text_frame.pack(side=TOP,fill=X)

            button_frame = Frame(top,bg='white')
            qb = Button(button_frame, text="Start", font='Helvetica', fg="white", bg=self.BUTTONS_BG)
            qb.pack( side = LEFT,pady=20,padx=20)
            dismiss_button = Button(button_frame, text="Dismiss", font='Helvetica', fg="white", bg=self.BUTTONS_BG, command=top.destroy)
            dismiss_button.pack( side= RIGHT, pady=20,padx=20)
            button_frame.pack(fill=X)

            code_frame = LabelFrame(top,bg='white',text="Authorization Code")
            code_frame_top = Frame(code_frame, bg='white')
            code_frame_top.pack(fill=X)
            code_frame_bot = Frame(code_frame, bg='white')
            code_frame_bot.pack(fill=X)
            auth_code = StringVar()
            code_entry = Entry(code_frame_top, textvariable = auth_code, font='Helvetica', width=40)
            self.__install_soft_keyboard(code_entry,auth_code)
            code_entry.pack(side=LEFT, padx=20, pady=20)
            paste_button = Button(code_frame_top,text="Paste",font='Helvetica',fg='white',bg=self.BUTTONS_BG, command = lambda *args: auth_code.set(self.clipboard_get()))
            paste_button.pack(side=RIGHT,padx=20,pady=20)

            ok_button = Button(code_frame_bot,text="Authenticate", font='Helvetica',fg='white',bg=self.BUTTONS_BG, command=top.destroy)
            ok_button.pack(fill=X,padx=20,pady=20)



            message_box = Text(text_frame, font=('Helvetica',10), height=12)
            message_box.insert(INSERT,"""You need to authorize this application to access you data

Click the Start button below:
    - This will launch a web browser
    - You will land on an authorization page for this app to
       - send emails
       - upload pictures
""")
            message_box.pack(fill=X)

            def authenticate():
                button_frame.pack_forget()
                code_frame.pack(fill=X, padx=10, pady=10)
                import webbrowser
                webbrowser.open(URI)

            qb.config(command=authenticate)


            self.wait_window(top)
            #update displayed
            print("returning code %s"%auth_code.get())
            return auth_code.get()
        print("Trying the connexion")
        #try to connect
        try:

            self.google_service = oauth2services.OAuthServices(constants.APP_ID_FILE,constants.CREDENTIALS_STORE_FILE,self.user_mail_var.get() )
            print(self.google_service.refresh())
        except Exception as error:
            self.google_service = None
            print(error)
            import traceback
            traceback.print_exc()
        self.__check_credentials_files()

    def __ask_for_removal(self,file,message):
        result = tkinter.messagebox.askquestion("Delete File", message, icon='warning')
        if result == 'yes':
            try:
                os.remove(file)
                print("%s deleted"%file)
            except:
                pass
        else:
            print("Canceled")
        #repaint the control
        self.__check_credentials_files()

    def __check_credentials_files(self):
        #empty current
        try:
            self.cred_store_frame.pack_forget()
            self.app_id_frame.pack_forget()
        except:
            pass
        has_app_id = os.path.exists(constants.APP_ID_FILE)
        #We shouldn't only check if the credential store is present
        #but ensure that it also is valid!
        #The following function creates a connection and detects a failure
        #It returns True if connection was ok and false otherwise
        def check_cred_store():
            #We use a special authorization callback handler that
            #raises an exception to stop the authorization process
            #This happens when credential store is missing or invalid
            def exception_handler(uri):
                raise ValueError("Bad credential file")
                return None
            try:
                #Try to connect to Google Services
                self.google_service = oauth2services.OAuthServices(constants.APP_ID_FILE,constants.CREDENTIALS_STORE_FILE,self.user_mail_var.get())
                return self.google_service.refresh()
            except Exception as error:
#                print error
#                import traceback
#                traceback.print_exc()
                #We failed to connect
                self.google_service = None
                return False

        has_cred_store = check_cred_store()

        self.app_id_frame = Frame(self.credentials_frame,bg='white')
        self.app_id_frame.pack(fill=X)
        self.cred_store_frame = Frame(self.credentials_frame,bg='white')
        self.cred_store_frame.pack(fill=X)
        if not has_app_id:
            self.app_id_label  = Label(self.app_id_frame, text="Application ID is missing", image=self.invalid_icon, compound=LEFT, font='Helvetica', bg='white')
            self.app_id_button = Button(self.app_id_frame, text="Get AppID", command=self.__get_app_id, font='Helvetica', fg='white',bg=self.BUTTONS_BG)
        else:
            self.app_id_label  = Label(self.app_id_frame, text="Application ID found", image=self.valid_icon, compound=LEFT, font='Helvetica', bg='white')
            self.app_id_button = Button(self.app_id_frame, text="Remove?", command=self.__remove_app_id, font='Helvetica', fg='white', bg=self.BUTTONS_BG)

        self.app_id_label.pack(side=LEFT,padx=20)
        self.app_id_button.pack(side=RIGHT,padx=20)

        if not has_cred_store:
            self.cred_store_label = Label(self.cred_store_frame, text = "Credential store is missing", image=self.invalid_icon, compound=LEFT, font='Helvetica', bg = 'white')
            self.cred_store_button = Button(self.cred_store_frame, text = "Connect", command=self.__connect_app, font='Helvetica', bg = self.BUTTONS_BG, fg='white')
        else:
            self.cred_store_label = Label(self.cred_store_frame, text = "Credential store found", image=self.valid_icon, compound=LEFT, font='Helvetica', bg = 'white')
            self.cred_store_button = Button(self.cred_store_frame, text = "Remove?", command=self.__remove_cred_store, font='Helvetica', bg = self.BUTTONS_BG, fg='white')

        self.cred_store_label.pack(side=LEFT,padx=20)
        self.cred_store_button.pack(side=RIGHT,padx=20)
        if not has_app_id:
            self.cred_store_button.config(state=DISABLED,bg=self.BUTTONS_BG_INACTIVE)
        else:
            self.cred_store_button.config(state=NORMAL,bg=self.BUTTONS_BG)

        if (not has_app_id) or (not has_cred_store):
            self.b_next.config(state=DISABLED, bg=self.BUTTONS_BG_INACTIVE)
        else:
            self.b_next.config(state=NORMAL, bg= self.BUTTONS_BG)


    def __decrement(self):
        """decrement by one page"""
        want_email = self.want_email_var.get() != 0
        want_upload = self.want_upload_var.get() != 0
        if self.page > 0:
            if self.page == 4 and not (want_email or want_upload):
                self.page = 0
            elif self.page == 4 and  not want_upload:
                self.page =2
            elif self.page == 3 and  not want_email:
                self.page = 1
            else:
                self.page -= 1
            self.__draw_page()


    def __increment(self):
        """increment by one page"""
        want_email = self.want_email_var.get() != 0
        want_upload = self.want_upload_var.get() != 0

        if self.page <= len(self.widgets):
            if self.page == 0 and not (want_email or want_upload):
                self.page = 4
            elif self.page == 1 and (not want_email):
                self.page= 3
            elif self.page == 2 and (not want_upload):
                self.page=4
            elif self.page == 4:
                self.page =4
            else :
                self.page +=1

            self.__draw_page()

    def __erase_page(self):
        """unpack all the widget currently displayed"""
        for widget in self.packed_widgets:
            widget.pack_forget()
        self.packed_widgets = []
        #update mail body at each page change (TODO : move this to an event)
        self.__mail_body_update_content()

    def __draw_page(self):
        """pack all the widgets corresponding to page self.page"""
        self.__erase_page()

        if self.page <= 0:
            self.page = 0
            self.b_prev.config(state=DISABLED)
            self.b_prev.config(bg=self.BUTTONS_BG_INACTIVE)
        else:
            self.b_prev.config(state=NORMAL)
            self.b_prev.config(bg=self.BUTTONS_BG)

        if self.page >= len(self.widgets)-1:
            self.page = len(self.widgets)-1
            self.b_next.configure(text="Save",command=self.__save_and_exit, bg=self.BUTTONS_BG_ACTION)
        else:
            self.b_next.config(state=NORMAL)
            self.b_next.configure(text="Next",command=self.__increment, bg=self.BUTTONS_BG)

        #regenerate credentials state
        if self.page == 1:
            self.__check_credentials_files()

        for w in self.widgets[self.page]:
            w.pack(fill=X,padx=20, pady=10)
            self.packed_widgets.append(w)

    def __save_and_exit(self):
        print("bye!")
        #finally create a personalized script to run the photobooth
        install_dir = os.path.split(os.path.abspath(__file__))[0]
        script_name = os.path.join(os.path.abspath(".."),"photobooth.sh")
        script = open(script_name,"w")
        script.write("#!/bin/sh\n")
        script.write("cd %s\n"% install_dir)
        script.write("python user_interface.py $* > %s\n"%(os.path.join(install_dir,"..","photobooth.log")))
        script.close()
        #make the script executable
        import stat
        st = os.stat(script_name)
        os.chmod(script_name, st.st_mode | stat.S_IEXEC)
        #write the configuration
        self.config.write()
        #exit assistant
        self.destroy()

    def __test_connection(self,test_email,test_upload):
        """Tests email sending and/or image uploading"""
        if (not test_email) and (not test_upload):
            return
        username = self.user_mail_var.get()
        if self.google_service is None:
            print("Unable to test service: no connection")
            return False

        # creating test image (a 32x32 image with random color)
        from PIL import Image
        from random import randint
        r=randint(0,255)
        g=randint(0,255)
        b=randint(0,255)
        im = Image.new("RGB", (32, 32), (r,g,b))
        im.save("test_image.png")
        if test_email:
            print("\nSending a test message to %s"%username)
            self.google_service.send_message(username,self.config.emailSubject,self.config.emailMsg,attachment_file="test_image.png")
        if test_upload:
            print("\nTesting picture upload in %s's album with id %s:"%(username,self.config.albumID))

            self.google_service.upload_picture("test_image.png", album_id = self.config.albumID)



def graphical_assistant():
    """Launches graphical interface"""
    try:
        config = configuration.Configuration('configuration.json')
        root = Assistant(config)
        try:
            root.geometry("450x400")
            root.mainloop()
        except:
            pass
    except:
        raise Exception("Graphical interface error")


def console_assistant():
    """Launches the text-based interface"""

    print("""
    ________________________________________________________________

    Welcome to the installation assistant!
    I will guide you through the setup and installation of Google
    credentials
    ________________________________________________________________

    """)
    install_dir = os.path.split(os.path.abspath(__file__))[0]


    #try to read configuration
    config = configuration.Configuration(constants.CONFIGURATION_FILE)



    config.enable_email = ask_boolean("Do you want the 'send photo by email' feature?",config.enable_email)
    print("")
    config.enable_upload = ask_boolean("Do you want the 'auto-upload photos' feature?",config.enable_upload)
    print("")
    config.enable_effects = ask_boolean("Do you want the 'Photos effects' feature?",config.enable_effects)
    print("")
    if printer_selection_enable == True:
        config.enable_print = ask_boolean("Do you want the 'Send photo to printer' feature?", config.enable_print)
        print("")
        if config.enable_print == True:
            conn = cups.Connection()
            printers = conn.getPrinters()
            index = 0
            selectedindex = 0
            for printer in printers:
                if config.selected_printer == str(index):
                    print('[*] ['+str(index)+'] '+printer)
                    selectedindex = index
                else:
                    print('[ ] ['+str(index)+'] '+printer)
                index = index + 1
            config.selected_printer = input("Seleted printer: [%s] confirm or change =>" % config.selected_printer)
            if config.selected_printer == "": config.selected_printer = selectedindex

    want_email  = config.enable_email
    want_upload = config.enable_upload
    want_print = config.enable_print
    selected_printer = config.selected_printer
    need_credentials = want_email or want_upload

    # We only need a user name if we need credentials
    if config.user_name is None:
        config.user_name = "foo@gmail.com"
    config.write()
    if need_credentials:
        # Check for user account
        _username = input("Google account: [%s] confirm or change => " % config.user_name)
        if _username != "":
            config.user_name = _username.strip()
            config.write()
        # Check for credentials
        app_id     = os.path.join(install_dir,constants.APP_ID_FILE)

        if os.path.exists(app_id):
            print("\n** found %s application file, will use it (remove in case of problems)"%constants.APP_ID_FILE)
        else:
            print("""
    ________________________________________________________________

    Photo upload or email sending requires that you create a
    Google Project and download the project's credentials to
    the scripts/ directory

    Note: you can do the following on any computer (except step 5/)
    ________________________________________________________________

    Here's a step by step guide:
    1/  Go to https://console.developers.google.com/start/api?id=gmail
    2/  Select "Create a project" and click continue
    3/  Follow the assistant with these hints:
        - Platform : other (with command-line user interface)
        - Access   : User data
        - Fill whatever your like for application name and ID name
    4/  The last step of the assistant makes you Download
        a client_id.json file : this is your project's credentials!
    5/  Copy the downloaded file to :
        %s

    The following page has up-to-date informations for this procedure:
    https://support.google.com/googleapi/answer/6158849

    The installation program will now exit.
    Run it again once this is done
    """%(app_id))
            sys.exit()

        # We do have the client_id !

        cred_store = os.path.join(install_dir,constants.CREDENTIALS_STORE_FILE)
        if os.path.exists(cred_store):
            print("\n** Found %s credential store"%constants.CREDENTIALS_STORE_FILE)
            remove_file = to_boolean(input("If you have troubles connecting you may want to remove this file\nRemove ? [N/y] => "),False)
            if remove_file:
                try:
                    os.remove(cred_store)
                except:
                    import traceback
                    traceback.print_exc()
                    print("\n==> Problem removing %s file, please do it on your side and run this assistant again\n"%cred_store)
                    sys.exit()

        # prepare the validation callback in case of missing or invalid credential store
        import webbrowser
        def auth_callback(authorization_uri):
            print("\n%s file is missing or invalid"%cred_store)
            print("""
    _________________________________________________________________

    You must authorize this application to access your data
    I will now open a web browser to complete the validation process
    Once this is done, you will get a validation key that you must
    paste below
    _________________________________________________________________""")
            input("Press a key when ready...")
            webbrowser.open(authorization_uri)
            mycode = input('\n[validation code]: ').strip()
            return mycode


        import oauth2services
        try:
            print("\n** Connecting...")
            service = oauth2services.OAuthServices(app_id,cred_store,config.user_name)
            connected = service.refresh() # will call 'auth_callback' if needed
            print("... Done")
        except Exception as error:
            print(error)
            print("\n==> Connection failed :(")
            sys.exit()

        if not connected:
            print("\nThere was an error during the connection")
            print("Please check your network connection and/or reauthorize this application")
            print("Exiting...")
            sys.exit()


       
        if config.albumID != None:
            keep_album = to_boolean(input("Photo Album is configured (%s), do you want to keep it? [Y/n] => "%config.album_name))
            change_album_id = not keep_album
        else:
            print("\nNo photo album selected, images will be uploaded to\nGoogle Photo Library (No Album)")
            change_album_id = to_boolean(input("\nDo you want to select another album for upload? [N/y] => "))

        if change_album_id:
            try:
                print("\nDownloading %s albums list..."% config.user_name)
                albums = service.get_user_albums()
                print("... %d albums found"%(len(albums)))
                candidates    = []
                candidates_id = []
                album_title = None
                album_id    = None
                while True:
                    search_string = input("Type a part of an existing album name (or return for all): ")
                    search_string = search_string.lower()
                    candidates    = ["<No Album>","<Create New>"]
                    candidates_id = ["","<New>"]
                    for album in albums:
                        title = album['title']
                        title_ = title.lower()
                        id    = album['id']
                        if title_.find(search_string) != -1:
                            candidates.append(title)
                            candidates_id.append(id)
                    if len(candidates) == 0:
                        print("Sorry: no match\n")
                    else:
                        break
                print("Here's the album that match:")
                for i, title in enumerate(candidates):
                    print("[%3d] %s"%(i,title))

                while True:
                    album_num = input("Type album number => ")
                    try:
                        album_title = candidates[int(album_num)]
                        album_id = candidates_id[int(album_num)]
                        break
                    except:
                        print("Bad album number!")
                if album_id == "":
                    config.albumID = None
                elif album_id == "<New>":
                    config.albumID = service.create_album(album_name = "TouchSelfie", add_placeholder_picture = True)
                    album_title = "TouchSelfie"
                else:
                    config.albumID = album_id
                config.album_name = album_title
                config.write()
                print("\nAlbum '%s' with id '%s' successfully selected!\n"%(album_title, album_id))
            except:
                import traceback
                traceback.print_exc()
                print("\n==> Error while fetching user albums, try to re-authenticate the application :(")


    # Optional tests for connection
    if config.enable_email:
        config.enable_email_logging = ask_boolean("Do you want to log outgoing email addresses?",config.enable_email_logging)
        config.write()
        test_email = to_boolean(input("Do you want to test email sending? [N/y] => "),False)

    if config.enable_upload:
        test_upload = to_boolean(input("Do you want to test image upload? [N/y] => "),False)

    test_connection(service, config, test_email, test_upload)

    #finally create a personalized script to run the photobooth
    script_name = os.path.join(os.path.abspath(".."),"photobooth.sh")
    script = open(script_name,"w")
    script.write("#!/bin/sh\n")
    script.write("cd %s\n"% install_dir)
    script.write("python user_interface.py $* > %s\n"%(os.path.join(install_dir,"..","photobooth.log")))
    script.close()
    #make the script executable
    import stat
    st = os.stat(script_name)
    os.chmod(script_name, st.st_mode | stat.S_IEXEC)

    print("""

    ________________________________________________________________

    We're all set, I just created a script to launch TouchSelfie with
    your options, you will find it here :
    => %s
    You can tune configuration parameters in scripts/%s
    You can adapt your hardware configuration in scripts/constants.py
    """% (script_name, constants.CONFIGURATION_FILE))


def to_boolean(answer, default=True):
    """Transforms a string to boolean"""
    if answer == '':
        return default
    if answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes':
        return True
    if answer == 'n' or answer == 'N' or answer == 'no' or answer == 'No':
        return False
    else :
        return False


def ask_boolean(prompt, current_value):
    """Returns a prompt suiting current_value"""
    if current_value:
        choice = "[Y/n]"
    else:
        choice = "[N/y]"
    return to_boolean(input("%s %s => "%(prompt,choice)),current_value)

def test_connection(service,config,test_email,test_upload):
    """Tests email sending and/or image uploading"""
    if (not test_email) and (not test_upload):
        return

    username = config.user_name

    # creating test image
    from PIL import Image
    im = Image.new("RGB", (32, 32), "red")
    im.save("test_image.png")
    if test_email:
        print("\nSending a test message to %s"%username)
        service.send_message(username,"oauth2 message sending works!","Here's the Message body",attachment_file="test_image.png")
    if test_upload:
        print("\nTesting picture upload in %s's album"%username)
        service.upload_picture("test_image.png", album_id = config.albumID)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--console", help="console mode, no graphical interface", action="store_true")
    args = parser.parse_args()

    if args.console:
        console_assistant()
    else:
        try:
            graphical_assistant()
        except Exception as error:
            print(error)
            #import traceback
            #traceback.print_exc()
            import time
            time.sleep(2)
            print("\nError loading graphical assistant, default to console based\n")
            console_assistant()
