import socket
import tkinter

name = socket.getfqdn()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
except OSError as e:
    ip = str(e)

def exit(*args):
    r.destroy()
r = tkinter.Tk()
r.geometry("+000+032")
r.overrideredirect(1)
tkinter.Label(r, text=name).pack()
tkinter.Label(r, text=ip).pack()
r.bind("<Button-1>", exit)
r.bind("<Key>", exit)
r.mainloop()


