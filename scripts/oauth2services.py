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
from googleapiclient.errors import HttpError

import logging
log = logging.getLogger(__name__)


class OAuthServices:
    """Unique entry point for Google Services authentication"""
    def __init__(self, client_secret, credentials_store, username, enable_upload = True, enable_email = True, log_level = logging.WARNING):
        """Create an OAuthService provider
        
        Arguments:
            client_secret (filename) : path to an application id json file with Gmail api activated (https://console.developers.google.com)
            credentials_store (filename) : path to the credentials storage (OK to put a nonexistent file)
            username                 : gmail address of the user whom account will be used
            enable_email             : enable send_email feature
            enable_upload            : enable upload pictures feature
            log_level                : level of logging (integer, see python module logging)     
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
            self.scopes += "https://www.googleapis.com/auth/photoslibrary.appendonly https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata "
        if self.enable_email:
            self.scopes += "https://www.googleapis.com/auth/gmail.send"
        self.scopes = self.scopes.strip()

        self.credential_store = file.Storage(credentials_store)
        
        log.setLevel(log_level)
        #mask googleapiclient info and debug messages, except in debug mode
        if (log_level == "DEBUG") or (log_level == logging.DEBUG):
            logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.INFO)
            logging.getLogger("googleapiclient.discovery").setLevel(logging.INFO)
        else:
            logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.WARNING)
            logging.getLogger("googleapiclient.discovery").setLevel(logging.WARNING)
                
        
    def refresh(self):
        """Refresh authentication
        
        returns: True if the refesh was successfull, False otherwise"""
        log.debug("refresh: Refreshing authentication token")
        if not (self.enable_email or self.enable_upload): # if we don't want features, just return
            log.debug("refresh: canceled: no service needed")
            return False
        cred = self.__oauth_login()
        if cred is None:    
            return False
        else:
            return True
    
    def __oauth_login(self):
        if not (self.enable_email or self.enable_upload): # if we don't want features, just return
            return None
        log.debug("__oauth_login: getting cached authentication token")
        credentials = self.credential_store.get()
        if credentials is None or credentials.invalid:
            log.warning("__oauth_login: No valid credentials found, starting authorization flow")
            try:
                flow = client.flow_from_clientsecrets(self.client_secret, self.scopes)
                credentials = tools.run_flow(flow, self.credential_store)
            except Exception as e:
                log.error("__oauth_login: Error authenticating")
                raise e

        if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
            log.debug("__oauth_login: caching period reached, refreshing token online")
            credentials.refresh(Http())

        self.credential_store.put(credentials)
        return credentials
    
    def __get_photo_client(self):
        if not self.enable_upload: #we don't want it
            return None
        credentials = self.__oauth_login()
        return build('photoslibrary', 'v1', http=credentials.authorize(Http()), cache_discovery=False)
        
    def create_album(self, album_name = "New Album", add_placeholder_picture = False):
        """ Create a new album in user's photo library
            RETURNS: albumId or None if there was an error
            ARGS: 
                album_name (str): the album name (deflt: "New Album")
                add_placeholder_picture (bool): add a small random colored placeholder image to the album (dflt: False)
        """
        log.debug("create_album: Creating album '%s' (placeholder image : %s)"%(album_name,str(True)))
        if not self.enable_upload:
            log.warning("create_album: Canceled album creation (enable_upload was set to False in constructor)")
            return {}
        client = self.__get_photo_client()
        try:
            res = client.albums().create(body={"album":{"title":album_name}}).execute()
            log.info("create_album: Album %s created with id: %s"%(album_name,res["id"]))
            if add_placeholder_picture:
                self.upload_picture("placeholder.png", album_id = res["id"], generate_placeholder_picture=True)
            return res["id"]
        except Exception as e:
            log.error("create_album: Error while creating album %s:"%str(e))
            return None
        

    def get_user_albums(self, as_title_id = True, exclude_non_app_created_data = True):
        """
        Retrieves connected user list of photo albums as:
            - a list({"title": "the title", "id":"jfqmfjqsjklfaz"}) if as_title_id argument is True (default)
            - the album list
        """
        log.debug("get_user_albums: Getting user photos albums")
        if not self.enable_upload:
            log.warning("get_user_albums: Canceled album fetching (enable_upload was set to False)")
            return {}
        client = self.__get_photo_client()
        albums = []
        try:
            log.debug("get_user_albums: Fetching first page of results")
            request = client.albums().list(pageSize=50,excludeNonAppCreatedData=exclude_non_app_created_data).execute()
            log.debug("get_user_albums: => %d albums found",len(request["albums"]))
            albums.extend(request["albums"])
            while (request.get("nextPageToken",None) is not None) and (len(request.get("albums",[])) == 50):
                log.debug("get_user_albums: Fetching next page of results")
                request = client.albums().list(pageSize=50, pageToken = request["nextPageToken"],excludeNonAppCreatedData=exclude_non_app_created_data).execute()
                log.debug("get_user_albums: => %d albums found",len(request["albums"]))
                albums.extend(request["albums"])
        except KeyError:
            #no albums
            log.error("get_users_album: Error while processing request")
            return albums
        except Exception as e:
            import json
            log.error("get_users_album: Error while processing request: %s"%str(e))
            raise(e)
            
        
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

    def upload_picture(self, filename, album_id = None , title="photo", caption = None, generate_placeholder_picture = False):
        """Upload a picture to Google Photos
        
        Arguments:
            filename (str) : path to the file to upload
            album_id (str) : id string of the destination album (see get_user_albums).
                if None (default), destination album will be Google Photos Library
            title (str)  DEPREC  : title for the photo (unused and deprecated)
            caption (str, opt) : a Caption for the photo
            generate_placeholder_picture (bool, opt, deflt: False) : 
                if set to True, <filename> picture won't be used and a 32x32 colored picture will be used instead
                This is usefull to create an album and upload a random picture to it so that it shows up in google photos
        """
        log.debug("upload_picture(%s, album_id = %s , title='%s', caption = %s, generate_placeholder_picture = %s)"%(filename,str(album_id),str(title), str(caption), str(generate_placeholder_picture)))
        if not self.enable_upload:
            log.debug("upload_picture: Canceled (service not configured)")
            return False
            
        client = self.__get_photo_client()
        creds = self.__oauth_login()
        
        # Step I: post file binary and get Token
        log.debug("upload_picture: Step I: uploading picture %s"%filename)
        file = os.path.basename(filename)
        url = 'https://photoslibrary.googleapis.com/v1/uploads'
        authorization = 'Bearer ' + creds.access_token

        headers = {
            "Authorization": authorization,
            'Content-type': 'application/octet-stream',
            'X-Goog-Upload-File-Name': file,
            'X-Goog-Upload-Protocol': 'raw',
        }
        http = creds.authorize(Http())
        
        try:
            if generate_placeholder_picture:
                log.debug("upload_picture: generating placeholder picture")
                from PIL import Image
                from random import randint
                # creating test image
                color = (randint(0,255),randint(0,255),randint(0,255))
                im = Image.new("RGB", (32, 32), color=color)
                import io
                with io.BytesIO() as output:
                    im.save(output, format="PNG")
                    filecontent = output.getvalue()
            else:
                with open(filename, "rb") as image_file:
                    filecontent=image_file.read()
            log.debug("upload_picture: uploading picture %s (%d bytes)"%(filename,len(filecontent)))
            (response,token) = http.request(url,method="POST",body=filecontent,headers=headers)
            if response.status != 200:
                log.warning("upload_picture: response code for upload %d != 200"%response.status)
                raise IOError("Error connecting to %s"%url)
            log.debug("upload_picture: Successfully uploaded image with id:[%s]"%token)

            # Step II: reference file Item
            if isinstance(caption,str):
                photo_item = {"simpleMediaItem": {"uploadToken": token}, "description": caption}
            else:
                photo_item = {"simpleMediaItem": {"uploadToken": token}}

            media_reference = dict(newMediaItems = [photo_item])
            if album_id is not None:
                media_reference["albumId"] = album_id
            
            import json;log.debug("upload_picture: referencing picture with id: [%s]\n %s"%(token, json.dumps(media_reference,indent=4)))
            try:
                try:
                    res = client.mediaItems().batchCreate(body=media_reference).execute()
                except HttpError as e:
                    if "Invalid album ID" in str(e):
                        log.error("upload_picture: album_id (%s) is not a valid album"%album_id)
                        log.warning("upload_picture: retrying to reference uploaded image without an album")
                        #Album is invalid, try to upload to user stream instead
                        res = client.mediaItems().batchCreate(body=dict(newMediaItems=[{"simpleMediaItem": {"uploadToken": token}}])).execute()
                if res["newMediaItemResults"][0]["status"]["message"] == "OK":
                    log.info("upload_picture: successfully uploaded image %s"%filename)
                    return True
                else:
                    log.warning("upload_picture: Unrecognized response")
                    return False

            except Exception as e:
                log.error("upload_picture: Error while referencing picture with id: %s (%s)"%(token,str(e)))
                return False
        except Exception as e:
            log.error("upload_picture: Error while uploading picture: (%s)"%str(e))
            return False
        return False
 
    def send_message(self,to, subject, body, attachment_file=None):
        """ send a message using gmail
        
        Arguments:
            to (str)      : email address of the recipient
            subject (str) : subject line
            body    (str) : body of the message
            attachment_file (str) : path to the file to be attached (or None)
        """
        log.debug("send_message(%s, '%s', '...', attachment_file=%s)"%(to, subject,str(attachment_file)))
        if not self.enable_email:
            log.debug("send_message: canceled (enable_email is False)")
            return False
        credentials = self.__oauth_login()
        http = credentials.authorize(Http())
        service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)
        
        log.debug("send_message: creating message")
        message = self.__createMessage(self.username, to, subject, body, body, attachment_file=attachment_file)
        
        try:
            log.debug("sending message")
            sent_message = (service.users().messages().send(userId="me", body=message).execute())
            log.info('send_message: successfully sent message with id: %s' % sent_message['id'])
            return True
        except errors.HttpError as error:
            log.error("send_message: An error occurred during send mail: %s" % error)
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
    logging.basicConfig()

    username = raw_input("Please enter your email address: ")
    
    # creating test image
    from PIL import Image
    #random color
    import random
    color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    
    im = Image.new("RGB", (32, 32), color=color)
    im.save("test_image.png")
    
    # Connecting to Google
    gservice = OAuthServices("client_id.json","storage.json",username,log_level=logging.DEBUG)


    print "\nTesting email sending..."
    print gservice.send_message(username,"oauth2 message sending works!","Here's the Message body",attachment_file="test_image.png")
    print "\nTesting album list retrieval..."
    albums = gservice.get_user_albums()
    for i, album in enumerate(albums):
        print "\t title: %s, id: %s"%(album['title'],album['id'])
        if i >= 10:
            print "skipping the remaining albums..."
            break
    print "\nTesting album creation and image upload"
    album_id = gservice.create_album(album_name="Test", add_placeholder_picture = True)
    print "New album id:",album_id
    print("Uploading to a bogus album")
    print(gservice.upload_picture("testfile.png",album_id = "BOGUS STRING" , caption="In bogus album", generate_placeholder_picture = True))
    

if __name__ == '__main__':
    test()
