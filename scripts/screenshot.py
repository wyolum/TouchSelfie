"""
A simple screen grabbing utility

@author Fabio Varesano - 
@date 2009-03-17
@modified by Justin Shaw
--- Changed filename to date
--- converted to linux
"""


import pyscreenshot as ImageGrab
import time
import datetime
import os

def snap(delay=0):
    now = datetime.datetime.now()
    Y = now.year
    M = now.month
    D = now.day
    h = now.hour
    m = now.minute
    s = now.second

    home = os.environ['HOME']
    pictures = os.path.join(home, 'Pictures')
    if not(os.path.exists(pictures)):
        os.mkdir(pictures)
    fn = "%4d-%02d-%02d_%02d%02d%02d.jpg" % (Y, M, D, h, m, s)
    fn = os.path.join(pictures, fn)
    ImageGrab.grab().save(fn, "JPEG")
    print 'saved', fn

if __name__ == '__main__':
    snap(delay=5)
