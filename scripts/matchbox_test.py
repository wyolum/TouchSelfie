import subprocess
from Tkinter import *

matchbox = None
def launch_matchbox():
    global matchbox
    if matchbox is None:
        matchbox = subprocess.Popen(["matchbox-keyboard"])
        b.config(command=kill_matchbox, text="kill")
        t.focus_set()
def kill_matchbox():
    global matchbox
    if matchbox is not None:
        matchbox.terminate()
        try:
            b.config(command=launch_matchbox, text="launch")
            matchbox = None
        except:
            pass


r = Tk()
l = Label(r, text="Matchbox-Keybaord!")
t = Entry(r, width=40);
b = Button(r, text="Launch", command=launch_matchbox)

l.pack()
b.pack()
t.pack()
r.mainloop()

kill_matchbox()
