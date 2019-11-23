from Tkinter import *

fn = "/sys/class/backlight/rpi_backlight/brightness"

def get_value():
    return int(open(fn).read())

def print_value(val):
    f = open(fn, 'w')
    f.write(val)
    f.close()

def exit(*args):
    master.destroy()

master = Tk()
master.geometry("+000+064")
master.overrideredirect(1)
master.bind("<Button-3>", exit)
w = Scale(master, from_=50, to=255, orient=HORIZONTAL, command=print_value)
w.set(get_value())
w.pack()
mainloop()
