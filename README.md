# Thanks to an *amazing* pull request from @laurentalacoque we now have a ton of new features!

Download and check them out!

# News! Now fully compatible with Google Photos API

Original version of TouchSelfie was based on the, now deprecated, PICASA web API.
The Picasa Web API is discontinued since January 2019.
This version of TouchSelfie handles the new API with the following conditions:

- You must enable 'Google Photos API' (and 'Gmail' if you want the 'send email' feature) on your [google developers console](https://console.developers.google.com). [See this article](https://github.com/laurentalacoque/TouchSelfie-extended/wiki/CreateGoogleProject) for help configuring your Google project and downloading your credentials file.
- You must download your app secret file to the following file : `scripts/google_client_id.json`
- You must relaunch the setup

### Difference with previous Picasa Web API

- This new API is safer and better for your privacy!
  - TouchSelfie only asks for the minimum amount of permission: it can only **append** photos and albums and only can access to items created by the application. This way, it makes it impossible for TouchSelfie to access informations or photos that you uploaded yourself
- This means that you can't select any album of your photo library, but your MUST create an album using the `setup.py` script. For this, just use the `Select Album` button and choose the `<Create new>` entry. (If you prefer to upload your photos in your photos library instead of an album as your camera does, just select `<No Album>` instead). Once your album is created, it will be populated with a random color square: don't remove it, otherwise this will delete the album)



# TouchSelfie
Open Source Photobooth forked and improved from [wyolum/TouchSelfie](https://github.com/wyolum/TouchSelfie)

For hardware construction, see [Make Magazine article](https://makezine.com/projects/raspberry-pi-photo-booth/)

## Take a shortcut:
- [Installation](#install)
- [What's new?](#changes)
- [A note on confidentiality and security](#confidentiality)

## <a id="install"></a>Installing (extracted and adapted from [Make Magazine](https://makezine.com/projects/raspberry-pi-photo-booth/))

### Complete Video Howto

For a very nice How-To of how to set up your photobooth, don't miss the video below!
Many thanks to [Caroline Dunn](http://carolinedunn.org/) for her great teaching skills.

[![Caroline Dunn's TouchSelfie installation howto](https://img.youtube.com/vi/Gd0RKYRNJmo/0.jpg)](https://www.youtube.com/watch?v=Gd0RKYRNJmo)


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
sudo pip install --upgrade oauth2client

# Install ImageMagick for the 'Animation' mode
sudo apt-get install imagemagick

# Install CUPS for the Printing function(optional)
sudo apt-get install cups
sudo apt-get install python-cups

# Setting up  CUPS/printer(optional)
https://www.techradar.com/how-to/computing/how-to-turn-the-raspberry-pi-into-a-wireless-printer-server-1312717
Test device:
Canon Selphy CP1300 with the Canon SELPHY CP900 - CUPS+Gutenprint v5.2.11  driver over USB

```

If google chrome is not on your system, the following might be necessary:

```
sudo apt-get install luakit
sudo update-alternatives --config x-www-browser
```
### Optional: create a Google project and enable the APIs
This is only needed if you plan to use the 'send email' or 'upload images to cloud' features of TouchSelfie.
[Here's an article](https://github.com/laurentalacoque/TouchSelfie-extended/wiki/CreateGoogleProject) that will help you creating a project and downloading its credentials

### Configure the program

1. run `setup.sh` script, this will:
  - guide you through the feature selection (email feature, upload feature)
  - Google Photos album selection
  - and will create a `photobooth.sh` launcher

2. `setup.sh` creates a configuration file `scripts/configuration.json`, you can edit this file to change configuration parameters, such as:
  - the logo file to put on your pictures
  - email subject and body
  - wether or not to archive snapshots locally
  - where to store pictures locally

3. Optionally you can change lower-level configuration options in the file `scripts/constants.py` such as:
  - captured image sizes
  - hardware dependent things




## <a id="changes"></a>Changes from [wyolum/TouchSelfie](https://github.com/wyolum/TouchSelfie)

### Zero password
- Now integrally based on OAuth2, neither the send-email, nor the upload-pictures will ask for and store a password. You will need to [create a Google project](https://github.com/laurentalacoque/TouchSelfie-extended/wiki/CreateGoogleProject) if you plan to use these features

### Send mails even from protected networks
- Many faculty/company networks block the sendmail port. By using OAuth2 authentication, photobooth emails are seen as https connection and are not blocked by the network anymore. (Again, [create a Google project](https://github.com/laurentalacoque/TouchSelfie-extended/wiki/CreateGoogleProject) for this)

### Easier setup
- a new `setup.sh` assistant will guide you through the configuration of the features you need (send_email, auto-upload) and will help you install the Google credentials.

### Hardware buttons support
- Added GPIO hardware interface for three buttons (with connections in hardware/ directory). Each button triggers a different effect. Software buttons are added if GPIO is not available. See `scripts/constants.py` to enable hardware buttons.

### Print selfies immediately
- A new 'print' button allows you to print selfies on a preconfigured printer (courtesy [Pikokosan](https://github.com/Pikokosan))

### New effects
- Added "Animation" effect that produces animated gifs (needs imagemagick)

![example animation](screenshots/anim.gif)

- Choose among `PiCamera` builtin image effects for more creative snapshots

![Effects Palette](screenshots/builtin-effects.png)

### Higher resolution pictures
- supports new v2.1 pi camera
- Supports arbitrary resolution for snapshots (configure it in constants.py)

### Better snap preview mode

- Preview now uses images for countdown: be creative! see `constants.py` for customizations.
- Preview is now horizontally flipped which is consistent with cameraphone behaviors and your bathroom mirror. (Previous mode was confusing for users)

### User interface improvements

- Modern "black" userinterface with icon buttons

![user interface](screenshots/new_user_interface.jpg?raw=true)


- New skinnable Touchscreen keyboard "mykb.py"

![new keyboard](screenshots/new_keyboard.jpg?raw=true)

- Removed configuration button to avoid pranks
  - use `setup.sh` to setup credentials and setup Google Photo Album
  - tune configuration in `constants.py`
  - limited runtime configuration (exit, enable/disable email and upload) is still possible via long press)

- snapshot display now supports animated gifs

- Mail address logging available in configuration
  - photobooth users can opt-out from the mail logging if activated

- command line arguments to enable/disable some features:
  - enable/disable fullscreen startup
  - enable/disable email sending
  - enable/disable auto-upload
  - enable/disable hardware buttons support (on-screen buttons displayed instead)
  - *Use `python user_interface.py --help` for a description of command line options*

## <a id="confidentiality"></a>A note on security and confidentiality

  - **During setup, you ask me to allow this application to access my email, the original TouchSelfie didn't do this, why?**

The Original TouchSelfie script used to store you google account and *password* in a `.credentials` file.

Considering it was a security risk, I prefered to code an alternate email-sending procedure that wouldn't require your password to get things done.

This is achieved via OAuth2 mechanism that only requires that you accept (once) that this application can access to your email. This way is safer since there's no way for the application to do anything other than what you accepted it to do.

  - **Wait, I don't want email sending, but you still ask me to accept that!**

To simplify the setup process, the setup assistant points you to a google credentials download page where email authorization is enabled by default. You can change this.

If you configured TouchSelfie to not send emails, you don't need to authorize access to your mail box, just change this during the credentials download process. This way, the application will only require basic authorization to your account.

  - **Will YOU have access to my emails?**

No, but don't take my word!

This is the beauty of opensource: everybody can read the source code and check if it's harmfull. Plus, with Github, you can't hide anything: every versions of this code is archived and I can't delete them: you will always be able to verify that I didn't do anything harmfull in the past.

Maybe you don't have the competency to verify the sourcecode, but others have and I trust they will alert the world if they find something nasty (or just file an [Issue!](../../issues)).

Hint for future verifyiers: the `scripts/oaut2services.py` contains all the code that accesses the Google Accounts. As you will see in the `__init__` method of the `OAuthServices` class, the only _scope_ that is requested it the `https://www.googleapis.com/auth/gmail.send` that restricts the permission of the application to only sending emails on your behalf. (See [this official doc](https://developers.google.com/gmail/api/auth/scopes#gmail_scopes))


  - **Will YOU have access to my photos?**
  
No, but again, don't take my word for it ;)
take a look at `scripts/oauth2services.py` where all Google account access are done. In the `__init__` method of the `OAuthServices` class, the only _scope_(s) that are requested for the photo library are:
 - `https://www.googleapis.com/auth/photoslibrary.appendonly` : can't browse for your photos or directories
 - `https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata`: can only access items created by _this_ app
 
See [official doc](https://developers.google.com/photos/library/guides/authentication-authorization#AboutAuthorization) for the Google Photos API scopes.



  - **Why do I need to create a project on Google Developers? Can't you provide one?**

Your Security and My Quota.

By retrieving yourself application credentials, you basically authorize yourself to access your own google account and you can revoke this whenever you want. Also, Application Credentials have a daily limit of free use, If I were to provide you my own credentials, a group of users would consume this quota in no time, leaving everybody with a bad experience.
