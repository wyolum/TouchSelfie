import os
from credentials import OAuth2Login

if __name__ == '__main__':
    email = "kevin.osborn@gmail.com"

    # options for oauth2 login
    configdir = os.path.expanduser('./')
    client_secrets = os.path.join(configdir, 'OpenSelfie.json')
    #client_secrets = os.path.join(configdir, 'client_secrets.json')
    credential_store = os.path.join(configdir, 'credentials.dat')

    gd_client = OAuth2Login(client_secrets, credential_store, email)
    
    albums = gd_client.GetUserFeed()
    for album in albums.entry:
       print 'title %s id =  %s' %(album.title.text, album.gphoto_id.text)
