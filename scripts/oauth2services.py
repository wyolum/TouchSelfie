"""
    Unification of email sending and album uploading using OAuth2Login
    Code for Google Photos / Picasa taken from "credentials.py" at https://github.com/wyolum/TouchSelfie
    Code for mail sending with OAuth2 taken from "apadana" at https://stackoverflow.com/a/37267330
    Assemblage and adaptation Laurent Alacoque 2o18
    
    - Update Jan 2019: Moving to photoslibrary API (Picasa API is now deprecated)
"""
import os
import base64
import httplib2
from apiclient import errors, discovery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import gdata
import gdata.photos.service
import gdata.media
import gdata.geo
import gdata.gauth
import webbrowser
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

class OAuthServices:
    """Unique entry point for Google Services authentication"""
    def __init__(self, client_secret, credentials_store, username, enable_upload = True, enable_email = True, authorization_callback = None):
        """Create an OAuthService provider
        
        Arguments:
            client_secret (filename) : path to an application id json file with Gmail api activated (https://console.developers.google.com)
            credentials_store (filename) : path to the credentials storage (OK to put a nonexistent file)
            username                 : gmail address of the user whom account will be used
            enable_email             : enable send_email feature
            enable_upload            : enable upload pictures feature
            authorization_callback   : a function callback that is responsible to connect to an authorization url, accept conditions and return a validation code (once)
                 prototype : mycallback(URI): connect(URI); code = raw_input('enter code:'); return code
                 by default a console callback is used, it automatically launches a webbrowser to the authorization URI and asks for a code in the console
        """
        self.client_secret = client_secret
        self.credentials_store = None
        self.username = username
        self.enable_upload = enable_upload
        self.enable_email  = enable_email
        self.scopes = ""
        
        if not (self.enable_email or self.enable_upload): # if we don't want features, just return
            return 

        #build scopes
        if self.enable_upload:
            self.scopes += "https://picasaweb.google.com/data/ "
        if self.enable_email:
            self.scopes += "https://www.googleapis.com/auth/gmail.send"
        self.scopes = self.scopes.strip()

        self.credential_store = Storage(credentials_store)
        
        if authorization_callback == None:
            def default_authorization_callback(authorization_uri):
                print "\nLaunching system browser to validate the credentials..."
                webbrowser.open(uri)
                code = raw_input('\nEnter the authentication code, then press Enter: ').strip()
                return code
            self.authorization_callback = default_authorization_callback
        else:
            self.authorization_callback = authorization_callback
                
        
    def refresh(self):
        """Refresh authentication
        
        returns: True if the refesh was successfull, False otherwise"""
        if not (self.enable_email or self.enable_upload): # if we don't want features, just return
            return False
        cred = self.__oauth_login()
        if cred is None:    
            return False
        else:
            return True
    
    def __oauth_login(self):
        if not (self.enable_email or self.enable_upload): # if we don't want features, just return
            return None
        credentials = self.credential_store.get()
        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(self.client_secret, scope=self.scopes, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            uri = flow.step1_get_authorize_url()
            code = self.authorization_callback(uri)
            credentials = flow.step2_exchange(code)

        if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
            http = httplib2.Http()
            http = credentials.authorize(http)
            credentials.refresh(http)

        self.credential_store.put(credentials)
        return credentials
    
    def __get_photo_client(self):
        if not self.enable_upload: #we don't want it
            return None
        credentials = self.__oauth_login()
        user_agent='picasawebuploader'
        return gdata.photos.service.PhotosService(source=user_agent,
                                                   email=self.username,
                                                   additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})

    def get_user_albums(self, as_title_id = True):
        """
        Retrieves connected user list of photo albums as:
            - a list({"title": "the title", "id":"jfqmfjqsjklfaz"}) if as_title_id argument is True (default)
            - a gdata userfeed otherwise
        """
        if not self.enable_upload:
            return {}
        client = self.__get_photo_client()
        albums = client.GetUserFeed()

        if as_title_id:
            #build a list of {"title": "My album Title", "id":"FDQAga124231"} elements
            album_list = []
            for album in albums.entry:
                entry = {}
                entry['title'] = album.title.text
                entry['id']    = album.gphoto_id.text
                album_list.append(entry)
            return(album_list)
        else:
            #full stuff
            return album.entry

    def upload_picture(self, filename, album_id = None , title="photo", caption = ""):
        """Upload a picture to Google Photos
        
        Arguments:
            filename (str) : path to the file to upload
            album_id (str) : id string of the destination album (see get_user_albums).
                if None (default), destination album will be Google Photos default 'Drop Box' album
            title (str)    : title for the photo (example : filename)
            caption (str, opt) : a Caption for the photo
        """
        if not self.enable_upload:
            return False
        
        if caption == None:
            caption =""
        
        if album_id == None:
            album_url = '/data/feed/api/user/default/albumid/default' # default folder
        else :
            album_url = '/data/feed/api/user/%s/albumid/%s' % (self.username, album_id)
        
        client = self.__get_photo_client()
        content_type, encoding = mimetypes.guess_type(filename)

        try:
            client.InsertPhotoSimple(album_url, title, caption, filename ,content_type=content_type)
        except Exception as error:
            print "Error uploading image %s",error
            return False
        return True
 
    def send_message(self,to, subject, body, attachment_file=None):
        """ send a message using gmail
        
        Arguments:
            to (str)      : email address of the recipient
            subject (str) : subject line
            body    (str) : body of the message
            attachment_file (str) : path to the file to be attached (or None)
        """
            
        if not self.enable_email:
            return False
        credentials = self.__oauth_login()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        message = self.__createMessage(self.username, to, subject, body, body, attachment_file=attachment_file)
        
        try:
            sent_message = (service.users().messages().send(userId="me", body=message).execute())
            print('Message Id: %s' % sent_message['id'])
            return True
        except errors.HttpError as error:
            print('An error occurred during send mail: %s' % error)
            return False
        return True

    def __createMessage(self,
        sender, to, subject, msgHtml, msgPlain, attachment_file=None):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          msgHtml: Html message to be sent
          msgPlain: Alternative plain text message for older email clients          
          attachmentFile (opt): The path to the file to be attached.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEMultipart('mixed')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        messageA = MIMEMultipart('alternative')
        messageR = MIMEMultipart('related')

        messageR.attach(MIMEText(msgHtml, 'html'))
        messageA.attach(MIMEText(msgPlain, 'plain'))
        messageA.attach(messageR)

        message.attach(messageA)

        #print("create_message_with_attachment: file: %s" % attachment_file)
        if attachment_file != None:
            content_type, encoding = mimetypes.guess_type(attachment_file)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            if main_type == 'text':
                fp = open(attachment_file, 'rb')
                msg = MIMEText(fp.read(), _subtype=sub_type)
                fp.close()
            elif main_type == 'image':
                fp = open(attachment_file, 'rb')
                msg = MIMEImage(fp.read(), _subtype=sub_type)
                fp.close()
            elif main_type == 'audio':
                fp = open(attachment_file, 'rb')
                msg = MIMEAudio(fp.read(), _subtype=sub_type)
                fp.close()
            else:
                fp = open(attachment_file, 'rb')
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(fp.read())
                fp.close()
            filename = os.path.basename(attachment_file)
            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string())}

def test():
    """ test email and uploading """
    username = raw_input("Please enter your email address: ")
    
    # creating test image
    from PIL import Image
    im = Image.new("RGB", (32, 32), "red")
    im.save("test_image.png")
    
    # Connecting to Google
    gservice = OAuthServices("client_id.json","mycredentials.dat",username)
    print "\nTesting email sending..."
    print gservice.send_message(username,"oauth2 message sending works!","Here's the Message body",attachment_file="test_image.png")
    print "\nTesting album list retrieval..."
    albums = gservice.get_user_albums()
    for i, album in enumerate(albums):
        print "\t title: %s, id: %s"%(album['title'],album['id'])
        if i >= 10:
            print "skipping the remaining albums..."
            break
    print "\nTesting picture upload"
    gservice.upload_picture("test_image.png")
    
    # test a new authorization call_back
    def myown_authorization_callback(authorization_uri):
        print "This is my own authorization callback!"
        print "I will launch a web browser for you to connect"
        print "Once connected, please enter the validation code below!"
        webbrowser.open(authorization_uri)
        mycode = raw_input('\n[code]: ').strip()
        return mycode
    alt_gservice = OAuthServices("client_id.json","new_cred.dat",username, authorization_callback = myown_authorization_callback)
    alt_gservice.get_user_albums()
    
    
    

if __name__ == '__main__':
    test()
