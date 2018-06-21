'''
    dummy classes to fake hardware (for test only)
    Laurent Alacoque 2o18
'''

from PIL import ImageDraw,ImageFont,Image

class Color:
    def __init__(self,color):
        self.color = color

class DummyPreview:
    def __init__(self):
        self.annotate_text = ""
class PiCamera:
    '''
    Thin wrapper for the cv2 camera interface to make it look like a PiCamera
    '''
    def __init__(self):
        self.hw_state = 0
        self.resolution = (800, 600)
        self.frame_counter = 0
        self.preview = DummyPreview()
        
    def start_preview(self):
        self.previewing = True
            
    def stop_preview(self):
        self.previewing = False
        
    def capture(self, filename, resize=None):
        im = Image.new('RGBA', self.resolution, (40,40,40,0))
        self.frame_counter = self.frame_counter + 1
        draw = ImageDraw.Draw(im)
        # draw text, half opacity
        try:
            fnt = ImageFont.truetype('arial.ttf', 80)
            draw.text((10,10), "[%d]"%self.frame_counter, font = fnt, fill=(255,255,255,128))
        except IOError:
            draw.text((10,10), "[%d]"%self.frame_counter, fill=(255,255,255,128))
        im = im.convert('RGB')
        im.save(filename)
        return True
    
    def capture_continuous(self, output):
        #'animframe-{counter:03d}.jpg'
        counter = 1
        while True:
            filename = output.format(counter=counter)
            self.capture(filename)
            yield filename
            counter += 1

            
    def close(self):
        del self.cam

        

if __name__ == '__main__':
    camera = Camera()
    camera.capture("out.jpg")
