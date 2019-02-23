from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
import json
import os.path
import argparse
import logging

def getAlbums(session, appCreatedOnly=False):

    params = {
            'excludeNonAppCreatedData': appCreatedOnly
    }

    while True:

        albums = session.get('https://photoslibrary.googleapis.com/v1/albums', params=params).json()

        logging.debug("Server response: {}".format(albums))

        if 'albums' in albums:

            for a in albums["albums"]:
                yield a

            if 'nextPageToken' in albums:
                params["pageToken"] = albums["nextPageToken"]
            else:
                return

        else:
            return

def create_or_retrieve_album(session, album_title):

# Find albums created by this app to see if one matches album_title

    for a in getAlbums(session, True):
        if not 'title' in a:
            continue
        if a["title"].lower() == album_title.lower():
            album_id = a["id"]
            logging.info("Uploading into EXISTING photo album -- \'{0}\'".format(album_title))
            return album_id

def save_cred(cred, auth_file):
    print('cred:', cred)
    cred_dict = {
        'token': cred.token,
        'refresh_token': cred.refresh_token,
        'id_token': cred.id_token,
        'scopes': cred.scopes,
        'token_uri': cred.token_uri,
        'client_id': cred.client_id,
        'client_secret': cred.client_secret
    }

    with open(auth_file, 'w') as f:
        print(json.dumps(cred_dict), file=f)

def auth(scopes):
    flow = InstalledAppFlow.from_client_secrets_file(
        'google_client_id.json',
        scopes=scopes)

    credentials = flow.run_local_server(host='localhost',
                                        port=8080,
                                        authorization_prompt_message="",
                                        success_message='The auth flow is complete; you may close this window.',
                                        open_browser=True)
    return credentials
def get_authorized_session(auth_token_file):

    scopes=['https://www.googleapis.com/auth/photoslibrary',
            #'https://www.googleapis.com/auth/photoslibrary.sharing',
            #'https://www.googleapis.com/auth/gmail.send'
    ]

    cred = None

    if auth_token_file:
        try:
            cred = Credentials.from_authorized_user_file(auth_token_file, scopes)
        except OSError as err:
            logging.debug("Error opening auth token file - {0}".format(err))
        except ValueError:
            logging.debug("Error loading auth tokens - Incorrect format")


    if not cred:
        cred = auth(scopes)

    session = AuthorizedSession(cred)
    print('session', session)
    if auth_token_file:
        try:            
            save_cred(cred, auth_token_file)
        except OSError as err:
            logging.debug("Could not save auth tokens - {0}".format(err))

    return session

def upload_photo(session, photo_file_name, album_id):

    #album_id = create_or_retrieve_album(session, album_name) if album_name else None

    # interrupt upload if an upload was requested but could not be created
    out = False

    session.headers["Content-type"] = "application/octet-stream"
    session.headers["X-Goog-Upload-Protocol"] = "raw"
    
    try:
        photo_file = open(photo_file_name, mode='rb')
        photo_bytes = photo_file.read()
    except OSError as err:
        return False

    session.headers["X-Goog-Upload-File-Name"] = os.path.basename(photo_file_name)

    logging.info("Uploading photo -- \'{}\'".format(photo_file_name))

    upload_token = session.post('https://photoslibrary.googleapis.com/v1/uploads', photo_bytes)

    if (upload_token.status_code == 200) and (upload_token.content):

        create_body = json.dumps({"albumId":album_id,
                                  "newMediaItems":[{"description":"","simpleMediaItem":
                                                    {"uploadToken":upload_token.content.decode()}}]}, indent=4)

        resp = session.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', create_body).json()

        logging.debug("Server response: {}".format(resp))

        if "newMediaItemResults" in resp:
            status = resp["newMediaItemResults"][0]["status"]
            if status.get("code") and (status.get("code") > 0):
                pass
            else:
                out = True
        else:
            pass

    else:
        pass

    try:
        del(session.headers["Content-type"])
        del(session.headers["X-Goog-Upload-Protocol"])
        del(session.headers["X-Goog-Upload-File-Name"])
    except KeyError:
        pass
    return True
def main():

    # session = get_authorized_session("auth_file")
    session = get_authorized_session("gphoto_credentials.dat")

    print(upload_photo(session, "img039.jpg", "TouchSelfie"))

if __name__ == '__main__':
  main()
