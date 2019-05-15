#!/bin/sh
### install TouchSelfie
## tested with fresh install of  raspian-stretch-full
sudo apt install -y python3-pil.imagetk
sudo pip3 install --upgrade google-api-python-client
sudo pip3 install --upgrade oauth2client
sudo pip3 install google_auth_oauthlib
mkdir /home/pi/code
cd /home/pi/code
git clone git://github.com/wyolum/TouchSelfie.git
git checkout python3
sudo apt install -y cups
sudo apt install -y libcups2-dev
sudo pip3 install pycups

curl https://get.pimoroni.com/onoffshim > install_onoffshim.sh
bash install_onoffshim.sh

# raspi-config ## enable camera
# python3 setup.py
# python3 user_interface.py 
