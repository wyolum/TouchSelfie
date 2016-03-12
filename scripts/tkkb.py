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

# r = Tk()
key_dim = 50
pad = 4
width=(len(button_labels[0]) + 2) * (key_dim + pad)
height=(len(button_labels) + 1) * (key_dim + pad)
fontsize = 24
offx = 10
offy = 10

class Key:
    keymaps = {}
    def __init__(self, can, label, shifted, bbox, entry, anchor='center', 
                 offx=offx, offy=offy, fontsize=fontsize):
        can.create_text(bbox[0] + offx, bbox[1] + offy, text=label, 
                        font=fontsize,
                        anchor=anchor, tag='lower')
        can.create_text(bbox[0] + offx, bbox[1] + offy, text=shifted, 
                        font=fontsize,
                        anchor=anchor, tag='upper')
        can.create_rectangle(bbox[0], bbox[1], 
                             bbox[2] + bbox[0], 
                             bbox[3] + bbox[1])
        self.bbox = bbox
        self.keymaps[label] = bbox
        self.label = label
        self.shifted = shifted
        self.entry = entry
        self.state = 'lower'
        self.c = can

    def onPress(self):
        if self.state == 'lower':
            self.entry.insert(END, self.label)
        else:
            self.entry.insert(END, self.shifted)


    def shift(self, state):
        self.state = state

class Shift(Key):
    def __init__(self, parent, *args, **kw):
        Key.__init__(self, *args, **kw)
        self.parent = parent

    def onPress(self):
        if self.state == 'lower':
            self.state = 'upper'
            self.c.itemconfig('lower', state=HIDDEN)
            self.c.itemconfig('upper', state=NORMAL)
        else:
            self.state = 'lower'
            self.c.itemconfig('upper', state=HIDDEN)
            self.c.itemconfig('lower', state=NORMAL)
        for row in self.parent.rows:
            for k in row:
                k.shift(self.state)
class Gmail(Key):
    def onPress(self):
        self.entry.insert(END, '@gmail.com')
        ## change labels to shifted keys
class BackSpace(Key):
    def onPress(self):
        p = self.entry.index(INSERT)
        if p > 0:
            self.entry.delete(p - 1)
        
class Tkkb:
    def __init__(self, r, entry):
        c = Canvas(r, width=width, height=height)
        c.pack()

        rows = []
        row = []
        for i, (l, s) in enumerate(top_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + pad,
                               pad,
                               key_dim, key_dim
                           ),
                           entry))
        rows.append(row)
        row = []
        for i, (l, s) in enumerate(second_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + .5 * (key_dim + pad),
                               1 * (key_dim + pad) + pad,
                               key_dim, key_dim
                           ),
                           entry))
        rows.append(row)
        row = []
        for i, (l, s) in enumerate(third_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + 1.0 * (key_dim + pad),
                               2 * (key_dim + pad) + pad,
                               key_dim, key_dim
                           ),
                           entry))
        rows.append(row)
        row = []
        for i, (l, s) in enumerate(bottom_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + 1.5 * (key_dim + pad),
                               3 * (key_dim + pad) + pad,
                               key_dim, key_dim
                           ),
                           entry))
        rows.append(row)

        shift = Shift(self, c, 'caps', 'CAPS',
                    (.5 * key_dim + pad, 4 * (key_dim + pad) + pad,
                     2.5 * (key_dim + pad), key_dim),
                    entry,
                    anchor='w', offx=5)
        space = Key(c, ' ', ' ',
                    (3.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,
                     4 * (key_dim + pad) - pad, key_dim),
                    entry)
        dotcom = Key(c, '.com', '.com',
                        (10.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,
                         2 * (key_dim + pad) - pad, key_dim),
                        entry,
                        offx=20,
                        fontsize=8)

        gmail = Gmail(c, '@gmail', '@gmail',
                        (7.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,
                         3 * (key_dim + pad) - pad, key_dim),
                      entry,
                    offx=30,
                      fontsize=8)
        rows.append([shift, space, gmail, dotcom])
        backspace = BackSpace(c, 'del', 'del',
                              (
                                  13 * (key_dim + pad) + pad,
                                  pad,
                                  2 * key_dim, key_dim
                              ),
                              entry, fontsize=3, anchor='center', offx=15)

        rows[0].append(backspace)

        c.itemconfig('upper', state=HIDDEN)
        entry.focus_set()            

        c.bind('<Button-1>', self.find_key)
        self.rows = rows
        self.c = c
        self.entry = entry

    def find_key(self, event):
        found = False
        ## find row
        for row in self.rows:
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


def main():
    r = Tk()
    entry = Entry(r, width=20, font=fontsize)
    entry.pack()

    Tkkb(r, entry)
    r.mainloop()

if __name__ == '__main__':
    main()

        

    
