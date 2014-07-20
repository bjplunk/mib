# source.py - adds the !source command to link the source of the bot

active_by_default = True
irc = None

def init(irc_handle):
    global irc
    irc = irc_handle

def source_callback(channel, usr, params):
    msg = "The source code for " + irc.nick + (" can be found at:"
    " https://github.com/ccshiro/mib")
    if channel != None:
        irc.chan_msg(channel, msg, user=usr)
    else:
        irc.priv_msg(usr, msg)

def get_commands():
    return [
        {'name': "source", 'type': "both", 'priv': 0, 'func': source_callback,
        'help': "links the github repository where you can find the source" +
        " code of this bot"}
    ]
