""" Generate image_effects snapshots based on effects/parameters defined in constants.py
    This basically takes snapshots as fast as possible, changing effects between two frames
    This is usefull if you change the IMAGE_EFFECTS constant and want to regenerate consistent images
"""

SNAP_PATH = "effects_snaps"
CROP_SIZE = 260 #cropsize of the thumbnail
DISPLAY_SIZE = 520
import os
import sys
sys.path.append(os.path.join('..','..'))
from constants import *
from time import sleep
from Tkinter import *
from PIL import Image,ImageTk

def snap_effects():
    """This takes snapshots of all the effects/parameters in constant IMAGE_EFFECTS"""
    try :
        os.mkdir(SNAP_PATH)
    except:
        pass
        
    import picamera
    camera = picamera.PiCamera()
    camera.start_preview()
    camera.annotate_text = "Get ready!"
    sleep(3)
    camera.annotate_text = ""
    effects_snaps ={}
    for effect in IMAGE_EFFECTS.keys():
        effect_name = IMAGE_EFFECTS[effect]["effect_name"]
        camera.image_effect = effect_name
        effect_string = effect_name
        if "effect_params" in IMAGE_EFFECTS[effect]:
            effect_params = IMAGE_EFFECTS[effect]["effect_params"]
            camera.image_effect_params = effect_params
            # add parameters to the effect string
            try:
                for arg in effect_params:
                    effect_string += "-" + str(arg)
            except:
                effect_string += "-" + str(effect_params)
        capture_filename = os.path.join(SNAP_PATH,effect_string + '.jpg')
        camera.capture(capture_filename)
        effects_snaps[effect] = capture_filename
    #all effects snapped
    return(effects_snaps)

def crop(effects_snaps):
    """this allows to tune the crop size and position"""
    try:
        ref_im_filename = effects_snaps['none']
    except:
        ref_im_filename = effects_snaps[effects_snaps.keys()[0]]

    ref_im = Image.open(ref_im_filename)
    
    root = Tk()
    splash=Image.new("RGB",(1,1))
    splash=ImageTk.PhotoImage(splash)
    
    label = Label(root,image=splash,width=DISPLAY_SIZE,height=DISPLAY_SIZE)
    
    global x_offset,y_offset
    x_offset= int((ref_im.size[0]-CROP_SIZE)/2)
    y_offset= int((ref_im.size[1]-CROP_SIZE)/2)
    
    def display_im():
        global x_offset,y_offset,splash
        cropped_im = ref_im.copy()
        cropped_im = cropped_im.crop((x_offset, y_offset, x_offset + CROP_SIZE, y_offset + CROP_SIZE))
        cropped_im = cropped_im.resize((DISPLAY_SIZE,DISPLAY_SIZE))
        splash = ImageTk.PhotoImage(cropped_im)
        label.configure(image=splash)
    label.pack()
    display_im()
    
    def keyboard_cb(event):
        global y_offset,x_offset
        if event.keysym == 'Up':
            y_offset -= 1
        elif event.keysym == 'Down':
            y_offset += 1
        elif event.keysym == 'Left':
            x_offset -= 1
        elif event.keysym == 'Right':
            x_offset += 1
        
        display_im()
        
        
    root.bind("<Up>",keyboard_cb)
    root.bind("<Down>",keyboard_cb)
    root.bind("<Left>",keyboard_cb)
    root.bind("<Right>",keyboard_cb)
    
    def validate_crop_cb(event):
        global y_offset, x_offset
        print "Cropping images at ",(x_offset,y_offset)
        crop_images(effects_snaps,x_offset,y_offset,'new_thumbs')
        root.destroy()
    root.bind("<Return>",validate_crop_cb)
    root.mainloop()
    
def crop_images(effects_snaps, offset_x, offset_y, path):
    """crop every image (values of dict 'effects_snaps') to size (CROP_SIZE x CROP_SIZE) and store them in 'path' directory with name IMAGE_EFFECTS[key]["effect_icon"]"""
    for effect in IMAGE_EFFECTS.keys():
        try:
            icon_fn = os.path.basename(IMAGE_EFFECTS[effect]["effect_icon"])
            snap_fn = effects_snaps[effect]
            full_image = Image.open(snap_fn)
            cropped_im = full_image.crop((offset_x, offset_y, offset_x + CROP_SIZE, offset_y + CROP_SIZE))
            try:
                os.mkdir(path)
            except:
                pass
            cropped_im.save(os.path.join(path,icon_fn))
        except Exception, err:
            print "Error generating crop for effect",effect
            print err

if __name__ == '__main__':
    effects_snaps = snap_effects()
    crop(effects_snaps)
