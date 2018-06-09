# TouchSelfie
Open Source Photobooth based on the official Raspberry Pi 7" Touchscreen

## Changes from wyolum/TouchSelfie

### Hardware buttons
- Added GPIO hardware interface for three buttons (with connections in hardware/ directory). Each button triggers a different effect. Software buttons are added if GPIO is not available

### New effects
- Added "Animation" effect that produces animated gifs (needs imagemagick)

### User interface improvements

- Modern "black" userinterface with icon buttons

- Preview now uses builtin annotate_text and opaque preview window

- New skinnable Touchscreen keyboard "mykb.py"

- Auto-hide configuration button (reactivate with tap on background)

- snapshot view now supports animated gifs
