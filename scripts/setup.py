import os.path
import sys



def assistant():    
    print """
    ________________________________________________________________

    Welcome to the installation assistant!
    I will guide you through the setup and installation of Google 
    credentials
    ________________________________________________________________

    """
    install_dir = os.path.split(os.path.abspath(__file__))[0]
    import configuration
    import constants

    #try to read configuration
    config = configuration.Configuration(constants.CONFIGURATION_FILE)



    config.enable_email = ask_boolean("Do you want the 'send photo by email' feature?",config.enable_email)
    print ""
    config.enable_upload = ask_boolean("Do you want the 'auto-upload photos' feature?",config.enable_upload)
    print ""

    want_email  = config.enable_email
    want_upload = config.enable_upload
    need_credentials = want_email or want_upload

    # We only need a user name if we need credentials
    if config.user_name is None:
        config.user_name = "foo@gmail.com"
    config.write()
    if need_credentials:
        # Check for user account
        _username = raw_input("Google account: [%s] confirm or change => " % config.user_name)
        if _username != "":
            config.user_name = _username.strip()
            config.write()
        # Check for credentials
        app_id     = os.path.join(install_dir,constants.APP_ID_FILE)
        
        if os.path.exists(app_id):
            print "\n** found %s application file, will use it (remove in case of problems)"%constants.APP_ID_FILE
        else:
            print """
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
    """%(app_id)
            sys.exit()
        
        # We do have the client_id !
        
        cred_store = os.path.join(install_dir,constants.CREDENTIALS_STORE_FILE)
        if os.path.exists(cred_store):
            print "\n** Found %s credential store"%constants.CREDENTIALS_STORE_FILE
            remove_file = to_boolean(raw_input("If you have troubles connecting you may want to remove this file\nRemove ? [N/y] => "),False)
            if remove_file:
                try:
                    os.remove(cred_store)
                except:
                    import traceback
                    traceback.print_exc()
                    print "\n==> Problem removing %s file, please do it on your side and run this assistant again\n"%cred_store
                    sys.exit()
        
        # prepare the validation callback in case of missing or invalid credential store
        import webbrowser
        def auth_callback(authorization_uri):
            print "\n%s file is missing or invalid"%cred_store
            print """
    _________________________________________________________________

    You must authorize this application to access your data
    I will now open a web browser to complete the validation process
    Once this is done, you will get a validation key that you must
    paste below
    _________________________________________________________________"""
            raw_input("Press a key when ready...")
            webbrowser.open(authorization_uri)
            mycode = raw_input('\n[validation code]: ').strip()
            return mycode
        
        
        import oauth2services
        try:
            print "\n** Connecting..."
            service = oauth2services.OAuthServices(app_id,cred_store,config.user_name, authorization_callback = auth_callback)
            connected = service.refresh() # will call 'auth_callback' if needed
            print "... Done"
        except Exception as error:
            print error
            print "\n==> Connection failed :("
            sys.exit()
            
        if not connected:
            print "\nThere was an error during the connection"
            print "Please check your network connection and/or reauthorize this application"
            print "Exiting..."
            sys.exit()
        
        # Successfully connected!
        if config.albumID != None:
            keep_album = to_boolean(raw_input("Photo Album is configured, do you want to keep it? [Y/n] => "))
            change_album_id = not keep_album
        else:
            print "\nNo photo album selected, images will be uploaded to\nGoogle Photo album 'Drop Box'"
            change_album_id = to_boolean(raw_input("\nDo you want to select another album for upload? [N/y] => "))
        
        if change_album_id:
            try:
                print "\nDownloading %s albums list..."% config.user_name
                albums = service.get_user_albums()
                print "... %d albums found"%(len(albums))
                candidates    = []
                candidates_id = []
                album_title = None
                album_id    = None
                while True:
                    search_string = raw_input("Type a part of an existing album name: ")
                    search_string = search_string.lower()
                    candidates    = []
                    candidates_id = []
                    for album in albums:
                        title = album['title']
                        title_ = title.lower()
                        id    = album['id']
                        if title_.find(search_string) != -1:
                            candidates.append(title)
                            candidates_id.append(id)
                    if len(candidates) == 0:
                        print "Sorry: no match\n"
                    else:
                        break
                print "Here's the album that match:"
                for i, title in enumerate(candidates):
                    print "[%3d] %s"%(i,title)
                
                while True:
                    album_num = raw_input("Type album number => ")
                    try:
                        album_title = candidates[int(album_num)]
                        album_id = candidates_id[int(album_num)]
                        break
                    except:
                        print "Bad album number!"
                config.albumID = album_id
                config.write()
                print "\nAlbum %s with id %s successfully selected!\n"%(album_title, album_id)
            except:
                import traceback
                traceback.print_exc()
                print "\n==> Error while fetching user albums, try to re-authenticate the application :("
            

    # Optional tests for connection
    if config.enable_email:
        test_email = to_boolean(raw_input("Do you want to test email sending? [N/y] => "),False)

    if config.enable_upload:
        test_upload = to_boolean(raw_input("Do you want to test image upload? [N/y] => "),False)
    
    test_connection(service, config, test_email, test_upload)
    
    #finally create a personalized script to run the photobooth
    options= ""
    if not want_email:
        options = options + "--disable-email "
    if not want_upload:
        options = options + "--disable-upload "
    script_name = os.path.join(os.path.abspath(".."),"photobooth.sh")
    script = open(script_name,"w")
    script.write("cd %s\n"% install_dir)
    script.write("python user_interface.py %s > %s\n"%(options,os.path.join(install_dir,"run.log")))
    script.close()

    print """
        
    ________________________________________________________________

    We're all set, I just created a script to launch TouchSelfie with
    your options, you will find it here :
    => %s
    You can tune configuration parameters in scripts/%s
    You can adapt your hardware configuration in scripts/constants.py
    """% (script_name, constants.CONFIGURATION_FILE)
    

def to_boolean(answer, default=True):
    if answer == '':
        return default
    if answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes':
        return True
    else :
        return False

        
def ask_boolean(prompt, current_value):
    if current_value:
        choice = "[Y/n]"
    else:
        choice = "[N/y]"
    return to_boolean(raw_input("%s %s => "%(prompt,choice)),current_value)
    
def test_connection(service,config,test_email,test_upload):
    if (not test_email) and (not test_upload):
        return
        
    username = config.user_name
    
    # creating test image
    from PIL import Image
    im = Image.new("RGB", (32, 32), "red")
    im.save("test_image.png")
    if test_email:
        print "\nSending a test message to %s"%username
        service.send_message(username,"oauth2 message sending works!","Here's the Message body",attachment_file="test_image.png")
    if test_upload:
        print "\nTesting picture upload in %s's album"%username
        service.upload_picture("test_image.png", album_id = config.albumID)


    
if __name__ == '__main__':
    assistant()
    
    
