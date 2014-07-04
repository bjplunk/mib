import irc, irc_msg

active_by_default = True
irc_handle = None

def init(irc):
    global irc_handle
    irc_handle = irc

def test_callback(user, params):
    arg = params.input if hasattr(params, 'input') else "none"
    for i in range(0, 25):
        irc_handle.chan_msg("#bot", str(i), user=user)

def get_commands():
    return [
        {'name': "test", 'type': "both", 'priv': 0, 'func': test_callback, 'args': ["input"], 'help': "just a bit of testing, really"}
    ]
