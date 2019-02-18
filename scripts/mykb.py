"""
    A stylable touchscreen keyboard for Tkinter
    Laurent Alacoque 2o18
    
    Constants:
    
    AZERTY_LAYOUT: An azerty keyboard layout
        list of keyboard rows of
            list of keys definitions
    * You are encouraged to create your own keyboard layouts and styles
    
        key definition examples: 
            letter a (shifted A) with default style
            [{'lower':  'a', 'upper': 'A'},{'styles':['default']}] 
            
            shift key labelled "shift" in both upper and lower states 
            with 2 times default key size 
            with styles "command" and "small"
            with special behavior "caps-lock" (see CapsLock(Key) class)
            [{'lower':  'shift', 'upper': 'shift'},{'styles':['command','small'], 'width':2.0, "special":"caps-lock"}],
            
    QWERTY_LAYOUT: A qwerty keyboard layout
        changes made from azerty
            qwerty key layout
            enter key displays "send"
            email addresses changes to common ".com"
        
    DEFAULT_STYLESHEET: an ordered list of styles element applied css-style to the elements
        style with "tag" "keyboard" allows to define the keyboard default style
 
            {    "tag": "keyboard",
                "background": "black",
                "keyboard-height": 400,
                "key-width": 62,
                "key-height": 62,
                "key-padding-horiz":5,
                "key-padding-vert":5
            }
        # Fonts for all keys:
            {    "tag": "key.text",
                "font": ("Helvetica",20,"bold"),
                "fill": "black",
            }
        # Redefine font for keys tagged 'small'
            {    "tag": "key.text.small",
                "font": ("Helvetica",14,"bold"),
            },


"""

import logging
log=logging.getLogger(__name__)

from Tkinter import *

class Key:
    """Implements common behavior for a Keyboard Key"""
    
    def __init__(self, keyboard, bound_entry, key_states, tags=[], bounding_box=(0,0,10,10)):

        """
        Constructor for the Key
        
        Creates a rectangle box on the keyboard canvas and add the letters (or strings) in key_states
        centered on the virtual key
        
        Arguments:
            keyboard (TouchKeyboard): The keyboard to which this key is attached
            bound_entry (Tk:Entry)  : An entry object to which to write
            key_states  (dict)      : the mode->value pairs for the key 
                (ex. key_state {"lower":"a", "upper":"A", "altgr":"@"}
            tags (list(str))        : a list of tags to help style the keys
            bounding_box (x,y,w,h)  : bounding_box in pixels
            
        Styling:
            styling is achieved with tag association
            each key letter is created using "key.text" tag
            each key letter is assigned it's state tag
            each key boundaries is created using "key.boundaries" tag
            each additional tags in the tags list are associated to these tags.
            for example the key 'lower':'a' with tags list ['default'] will have the following tags:
                'key.text'
                'key.text.default'
                'lower'
                'default'
            its drawn box will have the following tags:
                'key.boundaries'
                'key.boundaries.default'
                'default'
                
            
        """
        self.keyboard = keyboard
        canvas = keyboard.canvas
        # Create the bounding box as a rectangle, tag it key.boundaries
        my_boundary = canvas.create_rectangle(bounding_box[0], bounding_box[1], 
                                              bounding_box[2] + bounding_box[0], 
                                              bounding_box[3] + bounding_box[1], tags='key.boundaries')
        for tag in tags:
            canvas.addtag_withtag(tag,my_boundary) # Add all tags passed as arguments
        #print canvas.gettags(my_boundary)
        # also add tags as "key.boundaries.<tag>"
        for tag in tags:
            canvas.addtag_withtag("key.boundaries."+tag,my_boundary)
        # for each state ('upper', 'lower', 'ctrl', ...) add the corresponding text and tag it 'key.text'
        self.keys = {}
        for state in key_states:
            mykey = canvas.create_text(int(bounding_box[0]+bounding_box[2]/2),
                                       int(bounding_box[1]+bounding_box[3]/2), text=key_states[state], tags = ['key.text'])
            self.keys[state] = mykey
            # also add the state (e.g. 'lower') as tag to this key
            canvas.addtag_withtag(state,mykey)
            # also add all the tags passed as argument to this text
            for tag in tags:
                canvas.addtag_withtag(tag,mykey) # Add all tags passed as arguments
            for tag in tags:
                # also add 'key.text.<tag>' to this text
                canvas.addtag_withtag("key.text."+tag,mykey)
                #print "key.text."+tag
            self.bounding_box = bounding_box
            self.entry = bound_entry
        self.key_states  = key_states
        self.canvas = canvas
        self.current_value = ""
        self.mode = 'lower'
        
    def set_mode(self,mode):
        """Change current Key mode
        hide every key faces that aren't 'mode' show key face for mode 'mode'
        """
        self.mode = mode
        self.current_value = ""
        for state in self.key_states.keys():
            if state == mode:
                self.canvas.itemconfigure(state,state="normal")
                self.current_value = self.key_states[state]
            else: 
                self.canvas.itemconfigure(state,state="hidden")

    def react_to(self, event):
        """React to click event if click is inside the key"""
        if (event.x > self.bounding_box[0] and 
        event.x < self.bounding_box[0] + self.bounding_box[2] and
        event.y > self.bounding_box[1] and 
        event.y < self.bounding_box[1] + self.bounding_box[3]):
            #found !
            self.onPress()            
            return True
        else:
            return False

    def onPress(self):
        """callback to execute when key is pressed"""
        self.entry.insert(INSERT, self.current_value)

class CapsLockKey(Key):
    """Special Key that inherits from Key class
    
    toggle between Keyboard "upper" and "lower" modes
    """
    def onPress(self):
        if self.keyboard.current_mode == "upper":
            self.keyboard.set_mode("lower")
        else:
            self.keyboard.set_mode("upper")
            
class EnterKey(Key):
    """Special Key that inherits from Key class
    
    calls the Keyboard onEnter function
    """
    def __init__(self, keyboard, bound_entry, key_states, tags=None, bounding_box=(0,0,10,10), validator=None, variable=None):
        Key.__init__(self, keyboard, bound_entry, key_states, tags=tags + ['ENTER'], bounding_box=bounding_box)
        self.variable = variable
        self.validator = validator
        self.last_mode = 'lower'
        if self.variable is not None:
            self.variable.trace('w', self.onEntryChange)
        self.valid = True
        self.onEntryChange()
        
    def onEntryChange(self, *args, **kw):
        '''
        Change to normal text if valid
        '''
        s = self.entry.get().strip()
        new_valid = self.validate(s)
        
        if not self.valid and new_valid:
            for k in self.keys:
                self.canvas.itemconfig(self.keys[k],text=self.key_states[k])
            self.valid = True
        elif self.valid and not new_valid:
            for k in self.keys:
                self.canvas.itemconfig(self.keys[k],text="cancel")
            self.valid = False

    def validate(self, addr):
        out = True
        if self.validator is not None:
            out = bool(self.validator(addr))
        return out
    
    def onPress(self):
        if self.valid and self.keyboard.onEnter is not None:
            self.keyboard.onEnter()
        if not self.valid and self.keyboard.onCancel is not None:
            self.keyboard.onCancel()
            
class BackSpaceKey(Key):
    """Special Key that inherits from Key class
    
    delete a char in the bound_entry
    """
    def onPress(self):
        position = self.entry.index(INSERT)
        if position > 0:
            self.entry.delete(position - 1)


AZERTY_LAYOUT = [ 
    [
        [{'lower':  '1', 'upper': '1'},{'styles':['default']}],
        [{'lower':  '2', 'upper': '2'},{'styles':['default']}],
        [{'lower':  '3', 'upper': '3'},{'styles':['default']}],
        [{'lower':  '4', 'upper': '4'},{'styles':['default']}],
        [{'lower':  '5', 'upper': '5'},{'styles':['default']}],
        [{'lower':  '6', 'upper': '6'},{'styles':['default']}],
        [{'lower':  '7', 'upper': '7'},{'styles':['default']}],
        [{'lower':  '8', 'upper': '8'},{'styles':['default']}],
        [{'lower':  '9', 'upper': '9'},{'styles':['default']}],
        [{'lower':  '0', 'upper': '0'},{'styles':['default']}],
        [{'lower':  'del', 'upper': 'del'},{'styles':['command','small'], 'width':1.0, "special":"backspace"}],
        #[{'lower':  'enter', 'upper': 'enter'},{'styles':['command'], 'width':2.0, "special":"enter"}],
    ],
    [
        [{'lower':  'a', 'upper': 'A'},{'styles':['default']}],
        [{'lower':  'z', 'upper': 'Z'},{'styles':['default']}],
        [{'lower':  'e', 'upper': 'E'},{'styles':['default']}],
        [{'lower':  'r', 'upper': 'R'},{'styles':['default']}],
        [{'lower':  't', 'upper': 'T'},{'styles':['default']}],
        [{'lower':  'y', 'upper': 'Y'},{'styles':['default']}],
        [{'lower':  'u', 'upper': 'U'},{'styles':['default']}],
        [{'lower':  'i', 'upper': 'I'},{'styles':['default']}],
        [{'lower':  'o', 'upper': 'O'},{'styles':['default']}],
        [{'lower':  'p', 'upper': 'P'},{'styles':['default']}],
        [{'lower':  '.', 'upper': '.'},{'styles':['default']}],
    ],
    [

        [{'lower':  '?', 'upper': '#'},{'styles':['default']}],
        [{'lower':  'q', 'upper': 'Q'},{'styles':['default']}],
        [{'lower':  's', 'upper': 'S'},{'styles':['default']}],
        [{'lower':  'd', 'upper': 'D'},{'styles':['default']}],
        [{'lower':  'f', 'upper': 'F'},{'styles':['default']}],
        [{'lower':  'g', 'upper': 'G'},{'styles':['default']}],
        [{'lower':  'h', 'upper': 'H'},{'styles':['default']}],
        [{'lower':  'j', 'upper': 'J'},{'styles':['default']}],
        [{'lower':  'k', 'upper': 'K'},{'styles':['default']}],
        [{'lower':  'l', 'upper': 'L'},{'styles':['default']}],
        [{'lower':  'm', 'upper': 'M'},{'styles':['default']}],
    ],
    [

        [{'lower':  'shift', 'upper': 'shift'},{'styles':['command','small'], 'width':2.0, "special":"caps-lock"}],
        [{'lower':  'w', 'upper': 'W'},{'styles':['default']}],
        [{'lower':  'x', 'upper': 'X'},{'styles':['default']}],
        [{'lower':  'c', 'upper': 'C'},{'styles':['default']}],
        [{'lower':  'v', 'upper': 'V'},{'styles':['default']}],
        [{'lower':  'b', 'upper': 'B'},{'styles':['default']}],
        [{'lower':  'n', 'upper': 'N'},{'styles':['default']}],
        [{'lower':  '_', 'upper': '_'},{'styles':['default']}],
        [{'lower':  '-', 'upper': '-'},{'styles':['default']}],
        [{'lower':  '@', 'upper': '@'},{'styles':['default']}],
    ],
    [
        [{'lower':  '@free.fr', 'upper': '@orange.fr'},{'styles':['default','small'], 'width':2.0}],
        [{'lower':  ' ', 'upper': ' '},{'styles':['default'], 'width':4.0}],
        [{'lower':  '.fr', 'upper': '.com'},{'styles':['default', "small"]}],
        [{'lower':  '@gmail.com', 'upper': '@wanadoo.fr'},{'styles':['default','small'], 'width':2.0}],
        [{'lower':  'enter', 'upper': 'enter'},{'styles':['command','small'], 'width':2.0, "special":"enter"}],

    ]

]


QWERTY_LAYOUT = [ 
    [
        [{'lower':  '1', 'upper': '1'},{'styles':['default']}],
        [{'lower':  '2', 'upper': '2'},{'styles':['default']}],
        [{'lower':  '3', 'upper': '3'},{'styles':['default']}],
        [{'lower':  '4', 'upper': '4'},{'styles':['default']}],
        [{'lower':  '5', 'upper': '5'},{'styles':['default']}],
        [{'lower':  '6', 'upper': '6'},{'styles':['default']}],
        [{'lower':  '7', 'upper': '7'},{'styles':['default']}],
        [{'lower':  '8', 'upper': '8'},{'styles':['default']}],
        [{'lower':  '9', 'upper': '9'},{'styles':['default']}],
        [{'lower':  '0', 'upper': '0'},{'styles':['default']}],
        [{'lower':  'del', 'upper': 'del'},{'styles':['command','small'], 'width':1.0, "special":"backspace"}],
        #[{'lower':  'enter', 'upper': 'enter'},{'styles':['command'], 'width':2.0, "special":"enter"}],
    ],
    [
        [{'lower':  'q', 'upper': 'Q'},{'styles':['default']}],
        [{'lower':  'w', 'upper': 'W'},{'styles':['default']}],
        [{'lower':  'e', 'upper': 'E'},{'styles':['default']}],
        [{'lower':  'r', 'upper': 'R'},{'styles':['default']}],
        [{'lower':  't', 'upper': 'T'},{'styles':['default']}],
        [{'lower':  'y', 'upper': 'Y'},{'styles':['default']}],
        [{'lower':  'u', 'upper': 'U'},{'styles':['default']}],
        [{'lower':  'i', 'upper': 'I'},{'styles':['default']}],
        [{'lower':  'o', 'upper': 'O'},{'styles':['default']}],
        [{'lower':  'p', 'upper': 'P'},{'styles':['default']}],
        [{'lower':  '-', 'upper': '_'},{'styles':['default']}],
    ],
    [

        [{'lower':  'a', 'upper': 'A'},{'styles':['default']}],
        [{'lower':  's', 'upper': 'S'},{'styles':['default']}],
        [{'lower':  'd', 'upper': 'D'},{'styles':['default']}],
        [{'lower':  'f', 'upper': 'F'},{'styles':['default']}],
        [{'lower':  'g', 'upper': 'G'},{'styles':['default']}],
        [{'lower':  'h', 'upper': 'H'},{'styles':['default']}],
        [{'lower':  'j', 'upper': 'J'},{'styles':['default']}],
        [{'lower':  'k', 'upper': 'K'},{'styles':['default']}],
        [{'lower':  'l', 'upper': 'L'},{'styles':['default']}],
        [{'lower':  ';', 'upper': ':'},{'styles':['default']}],
        [{'lower':  '?', 'upper': '?'},{'styles':['default']}],
    ],
    [

        [{'lower':  'shift', 'upper': 'shift'},{'styles':['command','small'], 'width':2.0, "special":"caps-lock"}],
        [{'lower':  'z', 'upper': 'Z'},{'styles':['default']}],
        [{'lower':  'x', 'upper': 'X'},{'styles':['default']}],
        [{'lower':  'c', 'upper': 'C'},{'styles':['default']}],
        [{'lower':  'v', 'upper': 'V'},{'styles':['default']}],
        [{'lower':  'b', 'upper': 'B'},{'styles':['default']}],
        [{'lower':  'n', 'upper': 'N'},{'styles':['default']}],
        [{'lower':  'm', 'upper': 'M'},{'styles':['default']}],
        [{'lower':  '.', 'upper': '.'},{'styles':['default']}],
        [{'lower':  '@', 'upper': '@'},{'styles':['default']}],
    ],
    [
        [{'lower':  '@yahoo.com', 'upper': '@hotmail.com'},{'styles':['default','small'], 'width':2.0}],
        [{'lower':  ' ', 'upper': ' '},{'styles':['default'], 'width':4.0}],
        [{'lower':  '.com', 'upper': '.org'},{'styles':['default', "small"]}],
        [{'lower':  '@gmail.com', 'upper': '@aol.com'},{'styles':['default','small'], 'width':2.0}],
        [{'lower':  'send', 'upper': 'send'},{'styles':['command','small'], 'width':2.0, "special":"enter"}],

    ]

]


DEFAULT_STYLESHEET = [
    {    "tag": "keyboard",
        "background": "black",
        "keyboard-height": 400,
        "key-width": 65,
        "key-height": 65,
        "key-padding-horiz":5,
        "key-padding-vert":5
    },
    {    "tag": "key.text",
        "font": ("Helvetica",20,"bold"),
        "fill": "black",
    },
    {    "tag": "key.text.small",
        "font": ("Helvetica",14,"bold"),
    },
    {    "tag": "key.boundaries",
        "fill": "#cccccc",
        "outline": "white",
        "width": 3
    },
    {    "tag": "key.boundaries.command",
        "fill": "#888888",
    },
    {    "tag": "embedded-entry",
        "font": ("Helvetica",20)
    }
    #{    "tag": "key.boundaries.row-2",
        #"fill" : "white"
    #}

]

class TouchKeyboard:
    """a keyboard made out of rows of keys"""
    def __init__(self, Tkroot, bound_entry, onEnter = None, onCancel= None,
                 layout = QWERTY_LAYOUT, stylesheet = DEFAULT_STYLESHEET, validator=None):
        """Build a keyboard based on a layout and a stylesheet
        
        Arguments:
            Tkroot (TkWidget) : the root element in which we should build the keyboard
            bound_entry (TkEntry) or StringVar() : the textbox in which the key presses will be sent
                if this is a StringVar(), an Entry() will be created above the Keyboard
            onEnter               : callback function to call when Enter key is pressed
            onCancel               : callback function to call when Cancel key is pressed
            layout                : a list of list of key definitions that consitutes the keyboard layout
            stylesheet            : a list of directives for the keyboard styling
            validator             : changed Entry text to "Cancel" unless validor returns True [optional] #TJS
        """
        self.read_keyboard_stylesheet(stylesheet)
        self.validator = validator
        self.bound_entry = bound_entry
        if onEnter is None:
            def onEnter(*args, **kw):
                pass
        if onCancel is None:
            def onCancel(*args, **kw):
                pass
        self.onEnter = onEnter
        self.onCancel = onCancel

        # create a bound entry if needed
        try:
            bound_entry.winfo_class() #Will fail if this isn't a widget
            self.variable = None
        except:
            #if we fail, this means that this should be a stringvar
            # build an entry and link it to the variable
            log.warning("No bound Entry found: creating entry...")
            f = Frame(Tkroot)
            self.variable = bound_entry
            self.bound_entry = Entry(f,width=40, textvariable = self.variable, font='Helvetica')
            f.pack()
            self.bound_entry.pack()
            self.bound_entry.focus() ## TJS
        self.canvas = Canvas(Tkroot, width = self.keyboard_width, height=self.keyboard_height, background = self.keyboard_background)
        self.canvas.pack()
        self.keys = []
        self.Tkroot = Tkroot

        maxXPos=0;
        Ypos = self.padding_vert
        #For each Row
        for i, row in enumerate(layout):
            #add tag <row-#> to each key of the row
            rowtag = "row-" + str(i+1)
            #print "rowtag:",rowtag
            Xpos = self.padding_horiz
            #For each column
            for keydef, config in row:
                try:
                    styles=config['styles']
                except:
                    styles=[]
        
                width = self.key_width
                if "width" in config:
                    width_in_keys = config['width']
                    padding = 0
                    if width_in_keys > 1.0:
                        padding = int( (width_in_keys-1) * self.padding_horiz)
                    width = int(self.key_width * width_in_keys) + padding
                    #print "kw:",self.key_width," pad:", self.padding_horiz," total width : ",width
                
                Xpos += int((self.key_width + self.padding_horiz) * config.get('x-offset', 0))
                Ypos += int((self.key_height + self.padding_vert) * config.get('y-offset', 0))
                special = config.get('special', 'normal_key')

                bbox = (Xpos, Ypos, width, self.key_height)
                styles.append(rowtag)
                #print "width",width
                if special == "caps-lock":
                    self.keys.append(CapsLockKey(self, self.bound_entry, keydef, styles, bbox))
                elif special == "enter":
                    self.keys.append(EnterKey(self, self.bound_entry, keydef, styles, bbox, validator=self.validator, variable=self.variable))
                elif special == "backspace":
                    self.keys.append(BackSpaceKey(self, self.bound_entry, keydef, styles, bbox))
                else:
                    self.keys.append(Key(self, self.bound_entry, keydef, styles, bbox))
                Xpos += width + self.padding_horiz
                #print "new Xpos: %d"% Xpos
            else:
                maxXPos = Xpos
            Ypos += self.key_height + self.padding_vert
        # resize canvas
        self.canvas.configure(width = maxXPos, height = Ypos)
        self.apply_stylesheet(stylesheet)
        self.set_mode("lower")
    
        #install event handler
        self.canvas.bind('<Button-1>', self.dispatch_event)     # bind the click to the dispatcher
        self.canvas.bind('<Return>', self.onEnter)
        log.info("Keyboard created")

    def dispatch_event(self,event):
        """ dispatch a click event to every created key"""
        for key in self.keys:
            key.react_to(event)

    def set_mode(self,mode):
        """ change keyboard mode (lower/upper)
        This is normally done using a CapsLockKey() in the keyboard layout"""
        self.current_mode=mode
        for key in self.keys:
            key.set_mode(mode)

    def read_keyboard_stylesheet(self,stylesheet):
        """ Apply stylesheet to the 'keyboard' element (keys dimensions, ...)"""
        #read stylesheet for tag keyboard only
        self.keyboard_width = 800
        self.keyboard_height = 600
        self.key_width = 80
        self.key_height = 80
        self.padding_horiz = 10
        self.padding_vert = 10
        self.keyboard_background = ""
        try:
            for styledef in stylesheet:
                try:
                    if styledef['tag'] == "keyboard":
                        if "key-width" in styledef: self.key_width = styledef["key-width"]
                        if "key-height" in styledef: self.key_height = styledef["key-height"]
                        if "keyboard-width" in styledef: self.keyboard_width = styledef["keyboard-width"]
                        if "keyboard-height" in styledef: self.keyboard_height = styledef["keyboard-height"]
                        if "key-padding-horiz" in styledef: self.padding_horiz = styledef["key-padding-horiz"]
                        if "key-padding-vert" in styledef: self.padding_vert = styledef["key-padding-vert"]
                        if "background" in styledef: self.keyboard_background = styledef["background"]
                except:
                    pass
        except:
            pass
    def apply_stylesheet(self,stylesheet):
        """ Apply stylesheet list to the keyboard keys"""
        for styledef in stylesheet:
            try:
                tag = styledef["tag"]
                if tag == "keyboard": continue # we only style elements
                if tag == "embedded-entry":
                    if "font" in styledef:
                        self.bound_entry.configure(font=styledef["font"])
                    continue
                #print "Applying stylesheet for %s"%tag
                for  style in styledef.keys():
                    try:
                        if style == 'tag' : continue
                        #apply all styles to tag
                        value=styledef[style]
                        #print "\t",style,":", value
                        if style == "move":
                            self.canvas.move(tag,value[0],value[1])
                        elif style == "fill":
                            self.canvas.itemconfigure(tag,fill=value)
                        elif style == "font":
                            self.canvas.itemconfigure(tag,font=value)
                        elif style == "width":
                            self.canvas.itemconfigure(tag,width=value)
                        elif style == "outline":
                            self.canvas.itemconfigure(tag,outline=value)
                        elif style == "":
                            self.canvas.itemconfigure(tag,outline=value)
                        else:
                            log.error("Unknown style %s for tag %s"%(style,tag))
                    except:
                        pass
                self.canvas.update()
            except Exception, e:
                log.exception("Error while applying stylesheet")

__email_validator = re.compile(r'^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$')
def email_validator(addr):
    return bool(__email_validator.match(addr.strip()))

if __name__ == '__main__':
    r = Tk()
    myres = StringVar()
    def onEnter():
        print 'Enter Pressed'
        print "result %s"%myres.get()
    def onCancel():
        print 'Cancel Pressed'
        print "result %s"%myres.get()

    keyboard = TouchKeyboard(r,myres, onEnter = onEnter, onCancel=onCancel,
                             validator=email_validator)
    r.mainloop()
