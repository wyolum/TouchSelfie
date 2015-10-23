FILENAME = "EMAIL.LOG"

email_file = None

def log(name, email_address):
    global email_file
    if email_file is None or email_file.closed:
        email_file = open(FILENAME, "a")
    print >> email_file, '%s::%s' % (name, email_address)
    email_file.flush()
def log__test__():
    log("Justin Shaw", "wyojustin@gmail.com")
    log("WyoLum", "info@wyolum.com")
    email_file.close()
    f = open(FILENAME)
    print f.read()
    
