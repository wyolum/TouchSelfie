import os
import gdata
import gdata.photos.service
import gdata.media
import gdata.geo
import gdata.gauth
import webbrowser
import httplib2
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage


def OAuth2Login(client_secrets, credential_store, email):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    gd_client = GoogleDrive(gauth)

    return gd_client
