import subprocess
from Tkinter import *

matchbox = None
def launch_matchbox():
    global matchbox
    if matchbox is None:
        matchbox = subprocess.Popen(["matchbox-keyboard"])
        b.config(command=kill_matchbox, text="kill")
def kill_matchbox():
    global matchbox
    if matchbox is not None:
        matchbox.terminate()
        b.config(command=launch_matchbox, text="launch")
        matchbox = None


r = Tk()
l = Label(r, text="HERE")
b = Button(r, text="Matchbox!", command=launch_matchbox)

l.pack()
b.pack()
r.mainloop()
