from Tkinter import *

button_labels = ['`1234567890-=',
                 'qwertyuiop[]\\',
                 "asdfghjkl;'",
                 'zxcvbnm,./@'
             ]
shifted_labels = ['~!@#$%^&*()_+',
                  'QWERTYUIOP{}|',
                  'ASDFGHJKL:"',
                  'ZXCVBNM<>?@']

rows = []
for ls, ss in zip(button_labels, shifted_labels):
    rows.append(zip(ls, ss))

top_row, second_row, third_row, bottom_row = rows

r = Tk()
width=375
height=120
c = Canvas(r, width=width, height=height)
c.pack()
entry = Entry(r, width=20)
entry.pack()

key_dim = 20
pad = 4
fontsize=12
offx = 10
offy = 10

class Key:
    keymaps = {}
    def __init__(self, label, shifted, bbox, entry, anchor='center', 
                 offx=offx, offy=offy, fontsize=fontsize):
        c.create_text(bbox[0] + offx, bbox[1] + offy, text=label, 
                      font=fontsize,
                      anchor=anchor, tag='lower')
        c.create_text(bbox[0] + offx, bbox[1] + offy, text=shifted, 
                      font=fontsize,
                      anchor=anchor, tag='upper')
        c.create_rectangle(bbox[0], bbox[1], 
                           bbox[2] + bbox[0], 
                           bbox[3] + bbox[1])
        self.bbox = bbox
        self.keymaps[label] = bbox
        self.label = label
        self.shifted = shifted
        self.entry = entry
        self.state = 'lower'

    def onPress(self):
        if self.state == 'lower':
            self.entry.insert(END, self.label)
        else:
            self.entry.insert(END, self.shifted)


    def shift(self, state):
        self.state = state

def find_key(event):
    found = False
    ## find row
    for row in rows:
        if(event.y > row[0].bbox[1] and
           event.y < row[0].bbox[3] + row[1].bbox[1]):
             ## find key
            for key in row:
                if (event.x > key.bbox[0] and
                    event.x < key.bbox[2] + key.bbox[0]):
                    key.onPress()
                    found = True
                    break
        if found:
            break
    
    else:
        ### try special keys
        pass
    return found

c.bind('<Button-1>', find_key)

rows = []
row = []
for i, (l, s) in enumerate(top_row):
    row.append(Key(l, s,
                   (
                       (i + 1) * (key_dim + pad),
                       pad,
                       key_dim, key_dim
                   ),
                   entry))
rows.append(row)
row = []
for i, (l, s) in enumerate(second_row):
    row.append(Key(l, s,
                   (
                       (i + 1) * (key_dim + pad) + .5 * (key_dim + pad),
                       1 * (key_dim + pad) + pad,
                       key_dim, key_dim
                   ),
                   entry))
rows.append(row)
row = []
for i, (l, s) in enumerate(third_row):
    row.append(Key(l, s,
                   (
                       (i + 1) * (key_dim + pad) + 1.0 * (key_dim + pad),
                       2 * (key_dim + pad) + pad,
                       key_dim, key_dim
                   ),
                   entry))
rows.append(row)
row = []
for i, (l, s) in enumerate(bottom_row):
    row.append(Key(l, s,
                   (
                       (i + 1) * (key_dim + pad) + 1.5 * (key_dim + pad),
                       3 * (key_dim + pad) + pad,
                       key_dim, key_dim
                   ),
                   entry))
rows.append(row)

class Shift(Key):
    def __init__(self, *args, **kw):
        Key.__init__(self, *args, **kw)
    def onPress(self):
        if self.state == 'lower':
            self.state = 'upper'
            c.itemconfig('lower', state=HIDDEN)
            c.itemconfig('upper', state=NORMAL)
        else:
            self.state = 'lower'
            c.itemconfig('upper', state=HIDDEN)
            c.itemconfig('lower', state=NORMAL)
        for row in rows:
            for k in row:
                k.shift(self.state)
class Gmail(Key):
    def onPress(self):
        self.entry.insert(END, '@gmail.com')
        ## change labels to shifted keys
class BackSpace(Key):
    def onPress(self):
        l = len(self.entry.get())
        self.entry.delete(l-1, END)
        
shift = Shift('caps', 'CAPS',
            (1.5 * key_dim + pad, 4 * (key_dim + pad) + pad,
             2.5 * (key_dim + pad), key_dim),
            entry,
            anchor='w', offx=5)
space = Key(' ', ' ',
            (4.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,
             4 * (key_dim + pad) - pad, key_dim),
            entry)
dotcom = Key('.com', '.com',
                (11.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,
                 2 * (key_dim + pad) - pad, key_dim),
                entry,
                offx=20,
                fontsize=8)

gmail = Gmail('@gmail', '@gmail',
                (8.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,
                 3 * (key_dim + pad) - pad, key_dim),
              entry,
            offx=30,
              fontsize=8)
backspace = BackSpace('del', 'del',
                      (
                          14 * (key_dim + pad),
                          pad,
                          2 * key_dim, key_dim
                    ),
                      entry, fontsize=3, anchor='center', offx=15)

rows[0].append(backspace)
rows.append([shift, space, gmail, dotcom])

c.itemconfig('upper', state=HIDDEN)
entry.focus_set()            
r.mainloop()

        

    
