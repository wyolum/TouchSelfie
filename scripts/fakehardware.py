'''
    dummy classes to fake hardware (for test only)
    Laurent Alacoque 2o18
'''
import logging
log = logging.getLogger(__name__)

from PIL import ImageDraw,ImageFont,Image

class Color:
    """ Dummy Color class"""
    def __init__(self,color):
        self.color = color

class DummyPreview:
    """Dummy Preview class for camera.preview"""
    window=(0,0,640,480)
    def __init__(self):
        self.annotate_text = ""
class FakeOverlay:
    layer=0
    pass
class PiCamera:
    '''
    Fake PiCamera class to generate test images
    '''
    def __init__(self):
        """Constructor of a fake PiCamera

        Sets default values to populate the class properties
        """
        log.warning("Creating a dummy PiCamera: no real picture will be taken")
        self.hw_state = 0
        self.resolution = (800, 600)
        self.frame_counter = 0
        self.preview = DummyPreview()
        
    def start_preview(self):
        """does nothing"""
        self.previewing = True
        log.info("starting (fake) preview")
            
    def stop_preview(self):
        """does nothing"""
        self.previewing = False
        log.info("stoping (fake) preview")
        
    def capture(self, filename, resize=None):
        """Generate a new test image"""
        log.info("Generating dummy picture #%d"%self.frame_counter)
        im = Image.new('RGBA', self.resolution, (40,40,40,0))
        self.frame_counter = self.frame_counter + 1
        draw = ImageDraw.Draw(im)
        # draw text, half opacity
        try:
            fnt = ImageFont.truetype('arial.ttf', 80)
            draw.text((10,10), "[%d]"%self.frame_counter, font = fnt, fill=(255,255,255,128))
        except IOError:
            log.warning("font arial.ttf not found, using default")
            draw.text((10,10), "[%d]"%self.frame_counter, fill=(255,255,255,128))
        im = im.convert('RGB')
        im.save(filename)
        return True
        
    def add_overlay(self,overlay_image, size=(640,480)):
        log.info("faking overlay")
        return FakeOverlay()
        pass
        
    def remove_overlay(self,overlay):
        pass
        
    def capture_continuous(self, output):
        """Generate a sequence of test images"""
        #'animframe-{counter:03d}.jpg'
        counter = 1
        while True:
            filename = output.format(counter=counter)
            self.capture(filename)
            yield filename
            counter += 1

            
    def close(self):
        """Emulates PiCamera.close()"""
        del self.cam

        

if __name__ == '__main__':
    camera = Camera()
    camera.capture("out.jpg")
