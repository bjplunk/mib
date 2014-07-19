import dbm

active_by_default = False
irc = None
handouts = False
paste_link = ""

def get_account():
    lst = []

    try:
        with open("accounts") as f:
            lst = f.read().splitlines()
    except IOError:
        return None, None

    if len(lst) == 0:
        return None, None
    acc, pwd = lst[0].split(":", 1)
    lst = lst[1:]

    with open("accounts", "w") as f:
        for line in lst:
            f.write(line + "\n")

    return acc, pwd

def account_callback(chan, user, params):
    global handouts, paste_link
    if handouts == False:
        irc.priv_msg(user, "Account handouts are temporarily disabled. Please try again later.")
        return

    db = dbm.open("account", "c")
    if user.hostname.encode('utf-8') in db:
        irc.priv_msg(user, "Your hostname has already checked out an account (" + db[user.hostname.encode('utf-8')].decode('utf-8') + ")."
            " If you still need an account, please PM breadandbutter, nim or shiro.")
        db.close()
        return

    irc.priv_msg(user, "To get an account, please read the following paste: " + paste_link)
    db.close()

def give_acc(user):
    global handouts
    if handouts == False:
        irc.priv_msg(user, "Account handouts are temporarily disabled. Please try again later.")
        return
    db = dbm.open("account", "c")
    if user.hostname.encode('utf-8') in db:
        irc.priv_msg(user, "Your hostname has already checked out an account (" + db[user.hostname.encode('utf-8')].decode('utf-8') + ")."
            " If you still need an account, please PM breadandbutter, nim or shiro.")
        db.close()
        return
    
    acc, pwd = get_account()
    if acc == None:
        irc.priv_msg(user, "Sorry, the accounts are all out. Please try again next test.")
        db.close()
        return
    db[user.hostname.encode('utf-8')] = acc.encode('utf-8')
    irc.priv_msg(user, "Make sure to save your account details as you can only check out one account. Also, you can't recover the info if you lose it.")
    irc.priv_msg(user, "Your account is: " + acc + " Password: " + pwd)
    db.close()

def priv_msg(user, message):
    if message.lower().find("i have read and accept the content of the paste") == -1:
        return
    give_acc(user)

def handouts_callback(chan, user, params):
    global handouts, paste_link
    if params.state == "on":
        if params.paste == None:
            irc.priv_msg(user, "usage: !handouts on paste")
            return
        if handouts == True:
            irc.priv_msg(user, "Account handouts are already available")
        else:
            handouts = True
            paste_link = params.paste
            irc.priv_msg(user, "Account handouts turned ON")
    elif params.state == "off":
        if handouts == False:
            irc.priv_msg(user, "Account handouts is already off")
        else:
            handouts = False
            irc.priv_msg(user, "Account handouts turned OFF")
    else:
        irc.priv_msg(user, "pass on or off")

def init(irc_handle):
    global irc
    irc = irc_handle

def get_commands():
    return [
        {'name': "account", 'type': "both", 'priv': 0, 'func': account_callback,
        'help': "request a game account that will be used in the upcoming text, make sure to save the credentials as you can only request one account"},
        {'name': "handouts", 'type': "priv", 'priv': 100, 'func': handouts_callback,
        'args': ["state"], 'optargs': ["paste"], 'help': "toggle if people can check out accounts or not, pass on or off"}
    ]
