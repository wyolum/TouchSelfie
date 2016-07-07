import time
import numpy as np
import cv2

class Camera:
    '''
    Thin wrapper for the cv2 camera interface to make it look like a PiCamera
    '''
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        time.sleep(.3) ## wait for auto adjust
        self.led = False
        self.previewing = False
        
    def start_preview(self):
        pass
            
    def stop_preview(self):
        self.previewing = False
        
    def capture(self, filename, resize=None):
        '''
        resize not supported
        '''
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1600)
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,1200)
        ret, frame = self.cam.read()
        cv2.imwrite(filename, frame)
        
    def close(self):
        del self.cam

PiCamera = Camera

def test():
    cap = cv2.VideoCapture(0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print 'type "q" to quit'
    test()
