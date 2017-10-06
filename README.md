# TouchSelfie
Open Source Photobooth based on the official Raspberry Pi 7" Touchscreen

## Why use my fork?
My fork has been updated to use Google Drive via the `PyDrive`. If you read the comments on the [Make Magazine](http://makezine.com/projects/raspberry-pi-photo-booth/) article you can see there are a lot of issues with the Google Photos implementation, since this is FOSS I improved it.

The email sending feature was a little buggy. It would not allow another picture to be taken while the previous email picture was being sent. I use the `validate_email` library to sanitize input and break email sending into it's own thread. This makes everything much more seamless.

I created the `photobooth_gui_user.py` mode. This removes the `admin` features from the interface and only shows the email bar.

The `openselfie.conf` file has been expanded to include a `style` option that was previously hidden in the settings by a hardcoded value. An example can be seen below.
```
# Style of photo to take, options are:
#    * None   - Take a single picture
#    * Four   - Take four images and stitch them together
# Make sure to use a leading capitol letter!
style = Four
```

## Is it stable?
Yes, maybe even more than the original. I actually used it at my wedding and it worked flawlessly all night.

## Instructions
Follow the tutorial on [Make Magazine](http://makezine.com/projects/raspberry-pi-photo-booth/), but use this repo instead!

## What if I have an existing Photobooth setup?
You can keep all your configuration files! Just install `PyDrive` and  `validate_email`, then pull this code into your existing Photobooth folder.

## GoogleDrive Folder Selection
When you get the "Album ID Not Set" dialog you can try to list the albums from the customize pane. This doesn't seem to be 100% reliable at the moment though. As a fallback, open GoogleDrive, go into the album you want to use, and look at the URL. It should look like:
```
https://drive.google.com/drive/folders/S0m3RaNdoMNumb3rsAndLetTers
```
The last part of the URL, in this case `S0m3RaNdoMNumb3rsAndLetTers`, is the Album's ID. Copy and paste it into the customize dialog or in the `AlbumID` field of `openselfie.conf`
