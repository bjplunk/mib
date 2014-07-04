import time

import irc

class bot_cmd:
    def __init__(self, type, func, priv, args, optargs, help):
        self.type = type
        self.func = func
        self.priv = priv
        self.args = args
        self.optargs = optargs
        self.help = help

class cmd_params:
    pass

class commands:
    def __init__(self, irc):
        self.irc = irc
        self.cmds = {}

    # valid types: "chan", "priv", "both"
    def register_cmd(self, cmd, type, priv, func, args = [], optargs = [], help = ""):
        assert cmd not in self.cmds
        self.cmds[cmd] = bot_cmd(type, func, priv, args, optargs, help)

    def unregister_cmd(self, cmd):
        del self.cmds[cmd]

    def chan_msg(self, chan, user, msg):
        if msg[0] != self.irc.command_char:
            return

        i = msg.find(" ", 1)
        if i == -1:
            i = len(msg)

        cmd = msg[1:i]
        if i+1 < len(msg):
            msg = msg[i+1:]
        else:
            msg = ""

        if cmd not in self.cmds:
            return
        cmd_obj = self.cmds[cmd]

        if cmd_obj.type != "chan" and cmd_obj.type != "both":
            return

        # check so user has privileges for this command
        auth = self.irc.modules.get_module("auth")
        if not ((auth == None and cmd_obj.priv == 0) or auth.module.has_priv(user, cmd_obj.priv)):
            return

        # invoke command
        params = self.get_params(self.cmds[cmd], msg)
        if params != None:
            self.cmds[cmd].func(user, params)

    def priv_msg(self, user, msg):
        if msg[0] != self.irc.command_char:
            return

        i = msg.find(" ", 1)
        if i == -1:
            i = len(msg)

        cmd = msg[1:i]
        if i+1 < len(msg):
            msg = msg[i+1:]
        else:
            msg = ""

        if cmd not in self.cmds:
            return

        if self.cmds[cmd].type != "priv" and seld.cmds[cmd].type != "both":
            return

        # check so user has privileges for this command
        auth = self.irc.modules.get_module("auth")
        if not ((auth == None and cmd_obj.priv == 0) or auth.module.has_priv(user, cmd_obj.priv)):
            return

        # invoke command
        params = self.get_params(self.cmds[cmd], msg)
        if params != None:
            self.cmds[cmd].func(user, params)

    def next_arg(msg):
        i =  msg.find(" ")
        if i == -1:
            return msg, ""
        return msg[:i], msg[i:]

    def get_params(self, cmd, msg):
        params = cmd_params()

        for arg in cmd.args:
            if len(msg) == 0:
                # XXX: report error
                return None
            val, msg = commands.next_arg(msg)
            setattr(params, arg, val)

        for arg in cmd.optargs:
            val = None
            if len(msg) > 0:
                val, msg = next_arg(msg)
            setattr(params, arg, val)

        return params
