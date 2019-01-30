"""
    Unification of email sending and album uploading using OAuth2Login
    Code for Google Photos / Picasa taken from "credentials.py" at https://github.com/wyolum/TouchSelfie
    Code for mail sending with OAuth2 taken from "apadana" at https://stackoverflow.com/a/37267330
    Assemblage and adaptation Laurent Alacoque 2o18
    
    - Update Jan 2019: Moving to photoslibrary API (Picasa API is now deprecated)
"""
import os
import base64
from apiclient import errors, discovery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import webbrowser
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

class OAuthServices:
    """Unique entry point for Google Services authentication"""
    def __init__(self, client_secret, credentials_store, username, enable_upload = True, enable_email = True):
        """Create an OAuthService provider
        
        Arguments:
            client_secret (filename) : path to an application id json file with Gmail api activated (https://console.developers.google.com)
            credentials_store (filename) : path to the credentials storage (OK to put a nonexistent file)
            username                 : gmail address of the user whom account will be used
            enable_email             : enable send_email feature
            enable_upload            : enable upload pictures feature
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
            self.scopes += "https://www.googleapis.com/auth/photoslibrary "
        if self.enable_email:
            self.scopes += "https://www.googleapis.com/auth/gmail.send"
        self.scopes = self.scopes.strip()

        self.credential_store = file.Storage(credentials_store)
                
        
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
            flow = client.flow_from_clientsecrets(self.client_secret, self.scopes)
            credentials = tools.run_flow(flow, self.credential_store)

        if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
            credentials.refresh(Http())

        self.credential_store.put(credentials)
        return credentials
    
    def __get_photo_client(self):
        if not self.enable_upload: #we don't want it
            return None
        credentials = self.__oauth_login()
        return build('photoslibrary', 'v1', http=credentials.authorize(Http()))

    def get_user_albums(self, as_title_id = True):
        """
        Retrieves connected user list of photo albums as:
            - a list({"title": "the title", "id":"jfqmfjqsjklfaz"}) if as_title_id argument is True (default)
            - a gdata userfeed otherwise
        """
        if not self.enable_upload:
            return {}
        client = self.__get_photo_client()
        albums = []
        try:
            request = client.albums().list(pageSize=50).execute()
            albums.extend(request["albums"])
            while request.get("nextPageToken",None) is not None:
                print("loading next album page...")
                request = client.albums().list(pageSize=50, pageToken = request["nextPageToken"]).execute()
                albums.extend(request["albums"])
        except Exception as e:
            print("Error while fetching albums %s"%str(e))
            
        
        if as_title_id:
            #build a list of {"title": "My album Title", "id":"FDQAga124231"} elements
            album_list = []
            for album in albums:
                entry = {}
                #skip albums with no title
                if not ("title" in album.keys()):
                    continue
                entry['title'] = album.get("title")
                entry['id']    = album.get("id")
                album_list.append(entry)
            return(album_list)
        else:
            #full stuff
            return albums

    def upload_picture(self, filename, album_id = None , title="photo", caption = ""):
        """Upload a picture to Google Photos
        
        Arguments:
            filename (str) : path to the file to upload
            album_id (str) : id string of the destination album (see get_user_albums).
                if None (default), destination album will be Google Photos default 'Drop Box' album
            title (str)    : title for the photo (example : filename)
            caption (str, opt) : a Caption for the photo
        """
        #Not implemented
        raise NotImplementedError("upload_picture is not yet implemented")
        return False
 
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
        http = credentials.authorize(Http())
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
    gservice = OAuthServices("client_id.json","storage.json",username)
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

    
    
    

if __name__ == '__main__':
    test()
