"""
    Unification of email sending and album uploading using OAuth2Login
    Code for Google Photos / Picasa taken from "credentials.py" at https://github.com/wyolum/TouchSelfie
    Code for mail sending with OAuth2 taken from "apadana" at https://stackoverflow.com/a/37267330
    Assemblage and adaptation Laurent Alacoque 2o18
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


def OAuth2Login(client_secrets, credential_store, email , scope='https://picasaweb.google.com/data/'):
    storage = Storage(credential_store)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(client_secrets, scope=scope, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        uri = flow.step1_get_authorize_url()
        webbrowser.open(uri)
        code = raw_input('\nEnter the authentication code, then press Enter: ').strip()
        credentials = flow.step2_exchange(code)

    if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
        http = httplib2.Http()
        http = credentials.authorize(http)
        credentials.refresh(http)

    storage.put(credentials)

    return credentials

def get_photoservice_client(client_secrets,credential_store,email):
    credentials = OAuth2Login(client_secrets,credential_store,email,scope='https://picasaweb.google.com/data/')
    user_agent='picasawebuploader'
    return gdata.photos.service.PhotosService(source=user_agent,
                                                   email=email,
                                                   additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})




def SendMessage(sender, to, subject, msgHtml, msgPlain, credentials, attachmentFile=None):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else: 
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"

def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string())}

def createMessageWithAttachment(
    sender, to, subject, msgHtml, msgPlain, attachmentFile):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients          
      attachmentFile: The path to the file to be attached.

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

    print("create_message_with_attachment: file: %s" % attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(attachmentFile, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(attachmentFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(attachmentFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def main():
    to = "laurent.alacoque@gmail.com"
    sender = "laurent.alacoque@gmail.com"
    username="laurent.alacoque@gmail.com"
    subject = "email via oAuth"
    msgHtml = "Hi<br/>Html Email"
    msgPlain = "Hi\nPlain Email"
    
    print "Connecting to gmail and photos"
    creds = OAuth2Login("client_id.json", "mycredentials.dat", username, scope="https://picasaweb.google.com/data/ https://www.googleapis.com/auth/gmail.send")
    client = get_photoservice_client("client_id.json", "mycredentials.dat", username)

    print "Downloading albums"
    albums = client.GetUserFeed()
    print "\nFound %d albums in %s Photo Gallery"%(len(albums.entry),username)
    
    f = open("attachment.txt","w")
    for i,album in enumerate(albums.entry):
        title = album.title.text
        f.write(title + "\n")
        if i >= 9:
            break
    f.close()
    
    SendMessage(sender, to, subject, msgHtml, msgPlain, creds, attachmentFile='attachment.txt')

if __name__ == '__main__':
    main()