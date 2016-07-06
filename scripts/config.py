#set these up in your google account
import getpass
import os.path

install_dir = os.path.split(os.path.abspath(__file__))[0]
class Credential:
    def __init__(self):
        self.filename = os.path.join(install_dir, '.credentials')

        if os.path.exists(self.filename):
            f = open(self.filename)
            self.key = f.readline().strip()
            self.value = f.readline().strip()
        else:
            self.key = raw_input('Google Username:')
            self.value = getpass.getpass('App Specific Password')
            f = open(self.filename, 'w')
            f.write(self.key + '\n')
            f.write(self.value + '\n')

cred = Credential()
username = cred.key
password = cred.value
gmailUser = username
gmailPassword = password
