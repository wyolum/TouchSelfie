# Personalized effect thumbnails
If you happen to modify effects in `scripts/constants.py` or if you just want to personnalize the effect thumbnails, you might want to generate a new batch of effect thumbnails.

For this, just `python generate_effects_thumbnails.py` in front of your camera.
This will snap one photo by effect/parameters and will launch a cropper preview window.

In the preview window, just type <Up>, <Down>, <Left> or <Right> to center the crop where you want it and hit <Return>.

Crops will be generated in the `scripts/ressources/effects/new_thumbs` directory. If you're happy with what you got, just copy every thumbnails into the `scripts/ressources/effects` directory.

Voila, you just changed your effects thumbnails!
