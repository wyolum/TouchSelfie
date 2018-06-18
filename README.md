# TouchSelfie
Open Source Photobooth based on the official Raspberry Pi 7" Touchscreen


## Changes from [wyolum/TouchSelfie](https://github.com/wyolum/TouchSelfie)

### Easier setup
- a new `setup_credentials.sh` script will help you configure the features you need (send_email, auto-upload) and will guide you for the Google credentials setup.

### Hardware buttons support
- Added GPIO hardware interface for three buttons (with connections in hardware/ directory). Each button triggers a different effect. Software buttons are added if GPIO is not available

### New effects
- Added "Animation" effect that produces animated gifs (needs imagemagick)

### Higher resolution pictures
- supports new v2.1 pi camera
- Supports arbitrary resolution for snapshots (configure it in constants.py)

### User interface improvements

- Modern "black" userinterface with icon buttons

![user interface](/laurentalacoque/TouchSelfie/blob/master/screenshots/new_user_interface.jpg?raw=true)

- Preview now uses builtin annotate_text and opaque preview window

- New skinnable Touchscreen keyboard "mykb.py"

![user interface](/laurentalacoque/TouchSelfie/blob/master/screenshots/new_keyboard.jpg?raw=true)

- Auto-hide configuration button (reactivate with tap on background)

- snapshot view now supports animated gifs

- command line arguments to enable/disable some features:
  - enable/disable fullscreen startup
  - enable/disable email sending
  - enable/disable auto-upload

## Installing (extracted and adapted from [Make Magazine](https://makezine.com/projects/raspberry-pi-photo-booth/))

### Get the necessary packages

```
# update system 
sudo apt-get update

# Install ImageTk, Image from PIL
sudo apt-get install python-imaging
sudo apt-get install python-imaging-tk

# Install google data api and upgrade it
sudo apt-get install python-gdata
sudo pip install --upgrade google-api-python-client

# Install ImageMagick for the 'Animation' mode
sudo apt-get install imagemagick
```

If google chrome is not on your system, the following might be necessary:

```
sudo apt-get install luakit
sudo update-alternatives --config x-www-browser
```

### Install google credentials

You can now use the `setup_credentials.sh` script to guide you through the credentials retrieval and installation.


Now, for a bit of background: this application is able to send emails from your google account and upload picture in a Google Photos album

For this to work, you will need:
- One google account
- For email sending and Photos uploading: To enter your google account credentials in the application (It's safer to set your Google account to "double authentication" and use an "Application password" (see [instructions from Make Magazine](https://makezine.com/projects/raspberry-pi-photo-booth/)). For this, just launch the application: it will ask for a user/password.

  - Alternatively, you can create a `.credentials` file in the `/script/` directory with your google mail address on the first line and your password on the second line (yes, it's stored in clear :(, at least `chmod +600 .credentials` for a little privacy)

- For photos uploading: you will need to setup a new application on the [google developers console](https://console.developers.google.com/). Once this is done, you must download the application's credentials as a json file and move it to `scripts/OpenSelfie.json` (you can do this on your PC and simply copy it to your pi)

