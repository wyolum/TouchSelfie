from Tkinter import *

# keyboard layout
button_labels = ['`1234567890-=',
                 'qwertyuiop[]\\',
                 "asdfghjkl;'",
                 'zxcvbnm,./@'
             ]
shifted_labels = ['~!@#$%^&*()_+',
                  'QWERTYUIOP{}|',
                  'ASDFGHJKL:"',
                  'ZXCVBNM<>?@']

# Build the keyboard rows as tuples of (lowercase, uppercase) letters
rows = []
for ls, ss in zip(button_labels, shifted_labels):
    rows.append(zip(ls, ss))

top_row, second_row, third_row, bottom_row = rows


key_dim = 50    #  size of the keys in pixels (height and width)
pad = 4         # padding between keys
width=(len(button_labels[0]) + 2) * (key_dim + pad) # width of a full row (with 2 keys added)
height=(len(button_labels) + 1) * (key_dim + pad) # height of the 4 rows
fontsize = 18
offx = fontsize
offy = fontsize

class Key:
    keymaps = {}
    def __init__(self, can, label, shifted, bbox, entry, anchor='center', 
                 offx=offx, offy=offy, fontsize=fontsize):
        # create both an unshifted and a shifted key text with a rectangle
        can.create_text(bbox[0] + offx, bbox[1] + offy, text=label, 
                        font=("Helvetica", fontsize),
                        anchor=anchor, tag='lower')
        can.create_text(bbox[0] + offx, bbox[1] + offy, text=shifted, 
                        font=("Helvetica", fontsize),
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
        # when key is pressed, insert its label into the referenced Tk Entry
        if self.state == 'lower':
            self.entry.insert(INSERT, self.label)
        else:
            self.entry.insert(INSERT, self.shifted)


    def shift(self, state):
        self.state = state

class Shift(Key):
    # class shift inherits from Key
    def __init__(self, parent, *args, **kw):
        Key.__init__(self, *args, **kw)
        self.parent = parent

    def onPress(self):
        # onPress is redefined to reconfigure all canvas children visibility
        # the tag 'lower' and 'upper' are used to configure the visibility
        # every key has both a lower and upper tag text
        if self.state == 'lower':
            self.state = 'upper'
            self.c.itemconfig('lower', state=HIDDEN)
            self.c.itemconfig('upper', state=NORMAL)
        else:
            self.state = 'lower'
            self.c.itemconfig('upper', state=HIDDEN)
            self.c.itemconfig('lower', state=NORMAL)
        #Now that visibility is handled, reconfigure every key shift state
        for row in self.parent.rows:
            for k in row:
                k.shift(self.state)

## Special keys
                
# a special @gmail.com fast insert key                
class Gmail(Key):
    def __init__(self, *args, **kw):
        Key.__init__(self, *args, **kw)
    def onPress(self):
        self.entry.insert(INSERT, '@gmail.com')
        ## change labels to shifted keys
        
class Enter(Key):
    def onPress(self):
        if self.c.onEnter is not None:
            self.c.onEnter()
            
class BackSpace(Key):
    def onPress(self):
        p = self.entry.index(INSERT)
        if p > 0:
            self.entry.delete(p - 1)

# the mother class
class Tkkb:
    def __init__(self, r, entry, onEnter=None):
        # addon to pass a stringvar instead of an entry, in which case
        # we build our own entry in the keyboard
        try:
                entry.winfo_class() #Will fail if this isn't a widget
        except:
                #if we fail, this means that this should be a stringvar
                # build an entry and link it to the variable
                f = Frame(r)
                self.entry = Entry(f,width=40,textvariable = entry, font='Times')
                f.pack()
                self.entry.pack()
                entry=self.entry 
        # create canvas and add callback
        c = Canvas(r, width=width, height=height)
        c.pack()
        c.onEnter = onEnter

        rows = []
        row = []
        for i, (l, s) in enumerate(top_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + pad,     # left
                               pad,                                 # top
                               key_dim, key_dim
                           ),
                           entry))
        rows.append(row)
        row = []
        for i, (l, s) in enumerate(second_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + .5 * (key_dim + pad),    # half key from the left
                               1 * (key_dim + pad) + pad,                           # 1 row down
                               key_dim, key_dim
                           ),
                           entry))
        rows.append(row)
        row = []
        for i, (l, s) in enumerate(third_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + 1.0 * (key_dim + pad),   # two half-key shifts from the left
                               2 * (key_dim + pad) + pad,                           #2 rows down
                               key_dim, key_dim
                           ),
                           entry))
        if onEnter is not None:
            enter = Enter(c, 'Enter', 'Enter',
                          (12. * (key_dim + pad), 2 * (key_dim + pad) + pad,        # 14 keys from the left
                           2 * (key_dim + pad) - pad, key_dim),                     # 2 rows down
                          entry,
                          offx=30,
                          fontsize=12)
            row.append(enter)
        rows.append(row)
        row = []
        for i, (l, s) in enumerate(bottom_row):
            row.append(Key(c, l, s,
                           (
                               (i + 0) * (key_dim + pad) + 1.5 * (key_dim + pad),   #1.5 half-keys from the left
                               3 * (key_dim + pad) + pad,                           #3 rows down
                               key_dim, key_dim
                           ),
                           entry))
        rows.append(row)
## Fifth row special keys
        shift = Shift(self, c, 'caps', 'CAPS',
                    (.5 * key_dim + pad, 4 * (key_dim + pad) + pad,                 #.5 keys from the left / 4 rows down
                     2.5 * (key_dim + pad), key_dim),                               #2.5 keys wide
                    entry,
                    anchor='w', offx=5)
        space = Key(c, ' ', ' ',
                    (3.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,              #3.5 keys from the left / 
                     4 * (key_dim + pad) - pad, key_dim),                           #4 keys wide
                    entry)
        dotcom = Key(c, '.com', '.com',
                        (10.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,         #10.5 keys from the left / 4 rows down
                         2 * (key_dim + pad) - pad, key_dim),                       # 2 keys wide
                        entry,
                        offx=20,
                        fontsize=12)

        gmail = Gmail(c, '@gmail.com', '@gmail.com',
                        (7.5 * (key_dim + pad), 4 * (key_dim + pad) + pad,          #7.5 keys from the left / 4 rows down
                         3 * (key_dim + pad) - pad, key_dim),                       #3 keys wide
                      entry,
                      offx=60,
                      fontsize=12)
        rows.append([shift, space, gmail, dotcom])                                  # Append special keys
        backspace = BackSpace(c, 'backspace', 'backspace',
                              (
                                  13 * (key_dim + pad) + pad,                       #13 keys to the right
                                  pad,                                              # at the top row
                                  2 * key_dim, key_dim                              # 2 keys wide
                              ),
                              entry, fontsize=12, 
                              anchor='center', offx=45)

        rows[0].append(backspace)                                                   #Append on the first row

        c.itemconfig('upper', state=HIDDEN)     # hide uppercase letters    
        entry.focus_set()            

        c.bind('<Button-1>', self.find_key)     #on click/touch, launch findkey
        self.rows = rows
        self.c = c
        self.entry = entry

    # find which key is below the click and call its 'onPress' method
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
    def onEnter():
        print 'Enter Pressed'
    entry = Entry(r, width=20, font=fontsize)
    entry.pack()

    Tkkb(r, entry, onEnter=onEnter)
    r.mainloop()

if __name__ == '__main__':
    main()

        

    
