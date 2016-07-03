# Fabrication inputs
## 3D printing
Print camera_mount.stl, pi_stand2.stl, and 4 of the hex standoffs (hexstandoff.stl has 4 to print together. You can use the scad file to do them individually if you want.


PiCameraMount.stl and PiTouchScreenMount.stl are the new and improved tripod stand from the Make Magazine Article.

## Laser (Camera Mount)
The Camera mount gets screwed to the back of the top holes in the two stand legs. Cut it from 1/16" (1.5mm) acrylic

The pi camera takes 1.5mm screws, and I didn't have any so I just use double stick foam poster tape

##Assembly
* plug the pi and the touch screen board cables together
* insert the standoffs between the touch board and the Pi. Fasten with m2.5x20 screws to the touch screen.
* plug the camera cable into the pi, and thread through the slot in the camera mount. plug in to the camera, and fix with Poster tape.
* fasten camera mount to touch screen with m3x4 screws. If you're screws are too long, you can generate some standoffs of the appropriate size or pad with washer.
* put a 1/4-20 hex washer into the base.

If you are using a Raspberry Pi 2 (or earlier) you'll also need either ethernet or a wifi dongle for network connectivity. The Pi 3 has built in Wifi.