''' 
This is borrowed (and adapted) from Novel code here:
https://stackoverflow.com/questions/43770847/play-an-animated-gif-in-python-with-tkinter
Thanks!
'''
from Tkinter import *
from PIL import ImageTk,Image
from itertools import count

class ImageLabel(Label):
    def __init__(self, Tk_root, size=None):
        Label.__init__(self,Tk_root)
        self.size=size
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []
        w,h = im.size
        #compute resize ratio (fit image to size)
        ratio = 1.0
        if self.size is not None:
            ratio = max([ float(w)/self.size[0], float(h)/self.size[1]])
        try:
            for i in count(1):
                temp_frame = im.copy()
                temp_frame = temp_frame.resize(( int(w/ratio), int(h/ratio) ))
                self.frames.append(ImageTk.PhotoImage(temp_frame))
                if i == 1:
                    #immediately load first frame
                    self.config(image=self.frames[0])
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)
if __name__ == '__main__':

    root = Tk()
    lbl = ImageLabel(root,size=(300,300))
    def next_im():
        lbl.load('anim.gif')
    
    lbl.pack()
    lbl.load('photo.jpg')
    root.after(5000,next_im)
    root.mainloop()