# help module
# provides: !help <command> to print usage about any command available to the user

active_by_default = True
irc = None

def init(irc_handle):
    global irc
    irc = irc_handle

def help_callback(channel, user, params):
    if params.command == None or len(params.command) == 0:
        # Print all available commands for the user
        lst = [] # names of command
        for name, cmd in irc.commands.cmds.items():
            if not irc.has_privilege(user, cmd.priv):
                continue
            lst.append(name)
        lst.sort()
        irc.priv_msg(user, "Type " + irc.command_char + "help <command> to see more about a given command. Commands you have available are:")
        s = ""
        first = True
        for n in lst:
            tmp_str = s
            if not first:
                tmp_str += ", "
            first = False
            tmp_str += irc.command_char + n
            # make sure we can't overshoot irc's message length
            if len(tmp_str) >= 400:
                irc.priv_msg(user, s)
                s = "" + irc.command_char + n
            else:
                s = tmp_str
        if len(s) == 0:
            return
        irc.priv_msg(user, s)
    else:
        # Print info about specific command
        cmd_name = params.command[1:] if params.command[0] == irc.command_char else params.command
        if cmd_name not in irc.commands.cmds:
            irc.priv_msg(user, "There exists no such command.")
            return
        cmd = irc.commands.cmds[cmd_name]
        if not irc.has_privilege(user, cmd.priv):
            irc.priv_msg(user, "There exists no such command.")
            return
        s = irc.command_char + cmd_name
        for arg in cmd.args:
            s += " <" + arg + ">"
        for arg in cmd.optargs:
            s += " [" + arg +"]"
        irc.priv_msg(user, s)
        if len(cmd.help) > 0:
            irc.priv_msg(user, "description: " + cmd.help)

def get_commands():
    return [
        {'name': "help", 'type': "both", 'priv': 0, 'func': help_callback,
        'optargs': ["command"], 'help': "display help for bot commands"}
    ]
