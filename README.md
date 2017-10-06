# TouchSelfie
Open Source Photobooth based on the official Raspberry Pi 7" Touchscreen

## Instructions

Two additional libraries are required:
* `validate_email`
* `PyDrive`

I use a simple python library to check for valid email addresses.
To install [`validate_email`](https://pypi.python.org/pypi/validate_email)
```
sudo pip install validate_email
```

Use Google Drive instead of Google Photos.
To install [`PyDrive`](https://pypi.python.org/pypi/PyDrive/1.3.1_)
```
sudo pip install PyDrive
```

Then follow the tutorial on [Make Magazine](http://makezine.com/projects/raspberry-pi-photo-booth/)

## What if I have an existing Photobooth setup?
You can keep all your configuration files! Just install `PyDrive` and pull this code into your existing Photobooth folder.

## GoogleDrive Folder Selection
When you get the "Album ID Not Set" dialog you can try to list the albums from the customize pane. This doesn't seem to be 100% reliable at the moment though. As a fallback, open GoogleDrive, go into the album you want to use, and look at the URL. It should look like:
```
https://drive.google.com/drive/folders/S0m3RaNdoMNumb3rsAndLetTers
```
The last part of the URL, in this case `S0m3RaNdoMNumb3rsAndLetTers`, is the Album's ID. Copy and paste it into the customize dialog or in the `AlbumID` field of `openselfie.conf`
