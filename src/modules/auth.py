import dbm

active_by_default = True
irc = None
users = {} # logged in users, indexed on user.uid, value is privilege number

def init(irc_handle):
    global irc
    irc = irc_handle

def user_gone(user):
    if user.uid in users:
        del users[user.uid]

def login_user(channel, user, params):
    if user.uid in users:
        irc.priv_msg(user, "You're already logged in with an account. Use " + irc.command_char + "logout to logout.", 1)
        return

    if params.username == "root":
        if irc.root_pwd == "":
            irc.priv_msg(user, "No such username or password.", 1)
            return
        if params.password != irc.root_pwd:
            irc.priv_msg(user, "No such username or password.", 1)
            return
        priv = 100
    else:
        try:
            db = dbm.open("users", flag="r")
        except:
            irc.priv_msg(user, "No such username or password.", 1)
            return
        if params.username.encode('utf-8') not in db:
            irc.priv_msg(user, "No such username or password.", 1)
            db.close()
            return
        pwd, priv = db[params.username.encode('utf-8')].decode('utf-8').split(",", 1)
        if params.password != pwd:
            irc.priv_msg(user, "No such username or password.", 1)
            db.close()
            return
        db.close()

    # save user and priv level
    priv = int(priv)
    if priv >= 100 and params.username != "root":
        priv = 99
    users[user.uid] = priv
    irc.priv_msg(user, "You are now logged in as " + params.username + ".", 1)

def logout_user(channel, user, params):
    if user.uid not in users:
        irc.priv_msg(user, "You're not logged in.", 1)
        return
    del users[user.uid]
    irc.priv_msg(user, "You are now logged out.", 1)

def register_user(channel, user, params):
    db = dbm.open("users", flag="c")
    if params.password.find(",") != -1:
        irc.priv_msg(user, "Password cannot contain commas.", 1)
        db.close()
        return
    if params.username == "root" or params.username.encode('utf-8') in db:
        irc.priv_msg(user, "That username is already taken.", 1)
        db.close()
        return

    db[params.username.encode('utf-8')] = (params.password + ",0").encode('utf-8')
    irc.priv_msg(user, "Login registered correctly. Use " + irc.command_char + "login <username> <password> to log in.", 1)

def set_priv(channel, user, params):
    priv = int(params.priv)
    if priv >= 100:
        irc.priv_msg(user, "Priv must be in the range: [0,99].", 1)
        return
    try:
        db = dbm.open("users", flag="w")
    except:
        irc.priv_msg(user, "No such user.", 1)
        return
    if params.username not in users:
        irc.priv_msg(user, "No such user.", 1)
        return
    db[params.username.encode('utf-8')] = priv
    db.close()
    irc.priv_msg(user, "Changed privileges of " + params.username + " to " + str(priv) + ". Affected user needs to relog to obtain privileges.", 1)

def get_commands():
    return [
        {'name': "login", 'type': "priv", 'priv': 0, 'func': login_user,
        'args': ["username", "password"], 'help': "login to use protected commands"},
        {'name': "logout", 'type': "priv", 'priv': 0, 'func': logout_user, 'help': "log out from current user"},
        {'name': "register", 'type': "priv", 'priv': 0, 'func': register_user,
        'args': ["username", "password"], 'help': "register a username/password combination for use with " + irc.command_char + "login. "
            + "passwords are saved as plain-text; do not use a password you use anywhere else!"},
        {'name': "setpriv", 'type': "priv", 'priv': 100, 'func': set_priv,
        'args': ["username", "priv"], 'help': "set privilege of user, only available to root"}
    ]

def has_priv(user, priv):
    if priv == 0:
        return True
    if user.uid not in users:
        return False
    return users[user.uid] >= priv

