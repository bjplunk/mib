import irc, irc_msg

irc_handle = None

def init(irc):
    print("set irc handle")
    irc_handle = irc

def activate():
   print("activated") 

def deactivate():
    print("deactivated")

def raw_msg(msg):
    msg.debug_print()
