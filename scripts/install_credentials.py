import os.path
import sys
install_dir = os.path.split(os.path.abspath(__file__))[0]

def to_boolean(answer, default=True):
    if answer == '':
        return default
    if answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes':
        return True
    else :
        return False

print """
________________________________________________________________

Welcome to the credentials installation program!
I will guide you through the setup of your Google credentials
________________________________________________________________

"""
want_email = to_boolean(raw_input("Do you want the 'send photo by email' feature? [Y/n] => "))
print ""
want_upload = to_boolean(raw_input("Do you want the 'auto-upload photos' feature?  [Y/n] => "))
print ""

credfile   = os.path.join(install_dir, '.credentials')



have_user_name = False
username = ""
password = ""
if os.path.exists(credfile):
    try:
        f = open(credfile)
        username = f.readline().strip()
        password = f.readline().strip()
        f.close()
        have_user_name = True
        print "** Found credentials for user %s"%username
        keep_file = to_boolean(raw_input("Do you want to keep this file?\nAnswer no if you have problems sending emails [Y/n] => "))
        if not keep_file:
            have_user_name = False
            try:
                os.remove(credfile)
            except:
                import traceback
                traceback.print_exc()
                print "\n==> Problem removing %s file, please do it on your side and run this assistant again\n"%credfile
                sys.exit()
    except:
        print "File %s exists but I couldn't read it. You might want to delete it"%(credfile)
        sys.exit()
        
if (want_email or want_upload) and not have_user_name:
    print "You need a google account to which you will store your photos or from which you will send photos by email\n"
    username = raw_input("Enter your Google account address: ")
    username = username.strip()
    password = "xxxxxx" # don't need password if we don't use email
    if want_email:
        print "Additionally, email sending feature needs your account password, it will be stored locally."
        print "NOTE : You might want to set your Google account security settings to Double authentication and generate an application-specific password. This way, you can revoke access from your Google account withouth the hassles of a change of password"
        password = raw_input("Password for %s:"%username)
        password = password.strip()
    #Now create the .credentials file
    try:
        f = open(credfile, 'w')
        f.write(username + '\n')
        f.write(password + '\n')
        f.close()
        try:
            os.chmod(credfile, 0o600) #rw for owner only
        except:
            print "** Error changing permission to .credentials file, continuing\n"
    except:
        import traceback
        traceback.print_exc()
        print "\n==> Problem creating %s credential file, try to remove it and run this assistant again\n"
        sys.exit()

email_send_ok = False
if want_email:
    test_email = to_boolean(raw_input("Do you want to test email sending feature? [Y/n] =>"))
    if test_email:
        # first, create an attachment file
        f = open("test_attachment.txt","w")
        f.write("This is a simple attached file for test purpose only\n")
        f.close()
        # Send email with attached file
        try:
            import mailfile
            print "** Sending test message to %s. Check your inbox ;)\n"%username
            mailfile.sendMail(
                username,"[Test] email with attachment",
                "Hello, if you read this, you successfully configured the email sending feature :)",
                "test_attachment.txt", 
                from_account = username, 
                from_account_pass = password)
            email_send_ok = True
        except:
            import traceback
            traceback.print_exc()
            print "\n==> Error Sending Email to %s\n"%username

if want_upload:
    app_secret = os.path.join(install_dir, 'OpenSelfie.json')
    if os.path.exists(app_secret):
        print "** Found application credentials file OpenSelfie.json"
        keep_file = to_boolean(raw_input("Do you want to keep it? [Y/n] =>"))
        if not keep_file:
            try:
                os.remove(app_secret)
            except:
                import traceback
                traceback.print_exc()
                print "\n==> Problem removing %s file, please do it on your side and run this assistant again\n"%app_secret
                sys.exit()
                
    if not os.path.exists(app_secret):
        #Ask for user to create a project and download json
        print """
________________________________________________________________

Photo upload requires that you create a Google Application and
download the application's credentials to the scripts/ directory

Note: you can do the following on any computer (except step /11)
________________________________________________________________

Here's a step by step guide:
1/  Go to https://console.developers.google.com/
2/  Create a new project
3/  Wait a few minutes and select your newly create project
4/  Click on "Credentials" on the left
5/  In the popup window select "New Credentials" then "Oauth"
6/  If necessary, click on "configure your Consent Screen" and
    fill your project details then save this moves you back to 
    the Oauth ID creation page
7/  On the OAuth ID creation page, select "Other" as the application 
    type and fill a name
8/  A client OAuth window should popup, close it
9/  You should be back on the "Credentials" page with a listing of
    credentials for your project 
    This credentials listing should have at lease one line
    Click on the download icon at the right of the credential line
    to download your application's credentials
10/ You should now have a "client_secret_XXXXX.json" file in your 
    Downloads folder
11/ Just copy this file to the scripts/ directory of TouchSelfie.
    The script directory is at this location :
    %s

The following page has up-to-date informations for this procedure:
https://support.google.com/googleapi/answer/6158849

The installation program will now exit. Run it again once this is done
"""%install_dir
        sys.exit()
    
    # We found OpenSelfie.json
    
    credential_store = os.path.join(install_dir, 'credentials.dat')
    if os.path.exists(credential_store):
        print "** credentials.dat found\n"
        remove_file = to_boolean(raw_input("Do you want to re-authenticate your application? [Y/n] =>"))
        if remove_file:
            # Remove credentials.dat to avoid problems
            try:
                os.remove(os.path.join(install_dir,"credentials.dat"))
            except:
                pass
            print """
_________________________________________________________________

I will now launch a web browser so that you can authorize your
own application to access you own Google Photos Stream

Once authorized, Google will provide you with a validation code
Just copy the code from your browser and paste it in this terminal
window

Note: if no browser opens or you can't get the consent screen,
try to change your system browser to a google-supported one
_________________________________________________________________
"""
            raw_input("Press enter when ready...")
            
    
    try:
        import credentials
        client = credentials.OAuth2Login(app_secret, credential_store, username)
    except:
        import traceback
        traceback.print_exc()
        print "\n==> Error while connecting to Google :("
        sys.exit()
    #Test the connection
    try:
        print "\n Trying to download %s list of albums to test connection\n"%username
        albums = client.GetUserFeed()
        print "\nFound %d albums in %s Photo Gallery"%(len(albums.entry),username)
        candidates    = []
        candidates_id = []
        album_title = None
        album_id    = None
        while True:
            search_string = raw_input("Type a part of the destination album name: ")
            search_string = search_string.lower()
            candidates    = []
            candidates_id = []
            for album in albums.entry:
                title = album.title.text
                title_ = title.lower()
                id    = album.gphoto_id.text
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
                print "Bad album number"
        f = open("album.id","w")
        f.write(album_id)
        f.close()
        print "\nAlbum %s with id %s successfully selected!\n"%(album_title, album_id)
    except:
        import traceback
        traceback.print_exc()
        print "\n==> Error while fetching user albums, try to re-authenticate the application :("
        
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
"""% script_name
    

    
    
