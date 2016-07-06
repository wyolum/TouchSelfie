import tkkb
import os
from credentials import OAuth2Login
import Tkinter

class AlbumSelect:
    '''
    GUI to select an album from a list, update entry with album id
    '''
    fontsize=20
    def __init__(self, root, entrybox, entries):
        master = Tkinter.Toplevel(root)
        button_frame = Tkinter.Frame(master)
        list_frame = Tkinter.Frame(master)
        kb_frame = Tkinter.Frame(master)
        
        Tkinter.Button(button_frame, text="Reset", command=self.reset).pack(side=Tkinter.LEFT)
        Tkinter.Button(button_frame, text="Select",
                       command=self.select_and_push_result).pack(side=Tkinter.RIGHT)
        button_frame.pack()
        my_text = Tkinter.StringVar()
        my_text.trace('w', self.filter_entries)
        local_entry = Tkinter.Entry(list_frame, width=80, textvariable=my_text,
                                    font=self.fontsize)
        local_entry.pack()
        local_entry.bind('<Return>', self.push_result)
        local_entry.bind('<Down>', self.select_next)
        scrollbar = Tkinter.Scrollbar(list_frame)
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        self.listbox = Tkinter.Listbox(list_frame,
                                       yscrollcommand=scrollbar.set,
                                       width=80,
                                       height=5,
                                       font=self.fontsize)
        self.listbox.bind('<Double-Button-1>', self.picker)
        self.listbox.bind('<Return>', self.picker)
        self.all_entries = entries
        self.current_entries = self.all_entries
        self.update_list()
        self.listbox.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH)
        
        scrollbar.config(command=self.listbox.yview)

        self.master = master
        self.my_text = my_text
        self.local_entry = local_entry
        self.entrybox = entrybox
        self.scrollbar = scrollbar
        self.current = None
        self.local_entry.focus_set()
        
        kb_frame = Tkinter.Frame(master)
        kb = tkkb.Tkkb(kb_frame, local_entry)
        kb_frame.pack(side=Tkinter.TOP)

        button_frame.pack()
        list_frame.pack()
        kb_frame.pack(side=Tkinter.BOTTOM)
    def select_next(self, event):
        self.listbox.selection_set(0)
        self.listbox.focus_set()
        
    def picker(self, event=None):
        selected = self.listbox.curselection()
        if selected:
            idx = selected[0]
            choice = self.current_entries[idx]
            self.local_entry.delete(0, Tkinter.END)
            self.local_entry.insert(0, choice)
            self.local_entry.focus_set()
        else:
            choice = None
        return choice
    
    def select_and_push_result(self, event=None):
        choice = self.picker()
        if choice:
            self.push_result()
            
    def push_result(self, event=None):
        value = self.local_entry.get()
        id = value.split('::')[-1]
        if self.entrybox is not None:
            self.entrybox.delete(0, Tkinter.END)
            self.entrybox.insert(0, id)
        self.master.destroy()
        
    def update_list(self):
        self.listbox.delete(0, Tkinter.END)
        for entry in self.current_entries:
            self.listbox.insert(Tkinter.END, entry)

    def filter_entries(self, *args):
        text = self.local_entry.get()
        self.current_entries = [e for e in self.all_entries if text.lower() in e.lower()]
        self.update_list()
        if len(self.current_entries) == 1:
            self.listbox.selection_set(0)
        
    def reset(self, *args):
        self.local_entry.delete(0, Tkinter.END)
        self.filter_entries()
        self.update_list()
        
    def poll(self):
        now = self.listbox.curselection()
        if now != self.current:
            self.list_has_changed(now)
            self.current = now
        self.master.after(250, self.poll)

    def list_has_changed(self, selection):
        if selection:
            choice = self.current_entries[selection[0]]
            print 'selection is', choice
            self.local_entry.delete(0, Tkinter.END)
            self.local_entry.insert(Tkinter.END, choice)
        
def getAlbums(email):

    # options for oauth2 login
    configdir = os.path.expanduser('./')
    client_secrets = os.path.join(configdir, 'OpenSelfie.json')
    credential_store = os.path.join(configdir, 'credentials.dat')

    gd_client = OAuth2Login(client_secrets, credential_store, email)

    albums = gd_client.GetUserFeed()
    entries = []
    for album in albums.entry:
        title = album.title.text
        title = ''.join([c for c in title if ord(c) < 128])
        id = album.gphoto_id.text
        entry = '%s::%s' % (title, id)
        entries.append(entry)
    return entries

def test():
    if False:
        entries = getAlbums(email="kevin.osborn@gmail.com")
    else:
        entries = map(str, range(1000))

    root = Tkinter.Tk()
    entrybox = Tkinter.Entry(root, width=80)
    entrybox.pack()
    AlbumSelect(root, entrybox, entries)
    root.mainloop()
    
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'gui':
            test()
    else:
        for l in getAlbums(email="kevin.osborn@gmail.com"):
            print l
