import os
from credentials import OAuth2Login
import Tkinter

class AlbumSelect:
    '''
    GUI to select an album from a list, update entry with album id
    '''
    def __init__(self, root, entrybox, entries):
        master = Tkinter.Toplevel(root)
        my_text = Tkinter.StringVar()
        my_text.trace('w', self.filter_entries)
        local_entry = Tkinter.Entry(master, width=80, textvariable=my_text)
        local_entry.pack()
        local_entry.bind('<Return>', self.push_result)
        local_entry.bind('<Down>', self.select_next)
        scrollbar = Tkinter.Scrollbar(master)
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        self.listbox = Tkinter.Listbox(master, yscrollcommand=scrollbar.set, width=80)
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

    def select_next(self, event):
        self.listbox.selection_set(0)
        self.listbox.focus_set()
        
    def picker(self, event):
        selected = self.listbox.curselection()
        if selected:
            idx = selected[0]
            choice = self.current_entries[idx]
            self.local_entry.delete(0, Tkinter.END)
            self.local_entry.insert(0, choice)
            self.local_entry.focus_set()

    def push_result(self, event):
        self.entrybox.delete(0, Tkinter.END)
        value = self.local_entry.get()
        id = value.split('::')[-1]
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

    def poll(self):
        now = self.listbox.curselection()
        if now != self.current:
            # self.list_has_changed(now)
            self.current = now
        self.master.after(250, self.poll)

    def list_has_changed(self, selection):
        if selection:
            choice = self.current_entries[selection[0]]
            print 'selection is', choice
            self.local_entry.delete(0, Tkinter.END)
            self.local_entry.insert(Tkinter.END, choice)
        
def test(root, entrybox, entries):
    master = Tkinter.Frame(root)
    scrollbar = Tkinter.Scrollbar(master)
    scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

    listbox = Tkinter.Listbox(master, yscrollcommand=scrollbar.set)
    for i in range(100):
        listbox.insert(Tkinter.END, str(i))
    listbox.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH)

    scrollbar.config(command=listbox.yview)
    master.pack()


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

if __name__ == '__main__':
    if True:
        entries = getAlbums(email="kevin.osborn@gmail.com")
    else:
        entries = map(str, range(1000))

    root = Tkinter.Tk()
    entrybox = Tkinter.Entry(root, width=80)
    entrybox.pack()
    AlbumSelect(root, entrybox, entries)
    root.mainloop()
