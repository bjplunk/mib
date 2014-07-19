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

        if priv > 100:
            raise IndexError("Command privilege cannot exceed 100.")

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

    def chan_msg(self, channel, user, msg):
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

        if not self.irc.has_privilege(user, cmd_obj.priv):
            return

        # invoke command
        params = self.get_params(user, cmd_obj, msg)
        if params != None:
            print(self.irc.command_char + cmd + " invoked by " + user.nick + " in " + channel.name)
            cmd_obj.func(channel, user, params)

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
        cmd_obj = self.cmds[cmd]

        if cmd_obj.type != "priv" and cmd_obj.type != "both":
            return

        if not self.irc.has_privilege(user, cmd_obj.priv):
            return

        # invoke command
        params = self.get_params(user, cmd_obj, msg)
        if params != None:
            print(self.irc.command_char + cmd + " invoked by " + user.nick + " in PM")
            cmd_obj.func(None, user, params)

    def next_arg(msg):
        i =  msg.find(" ")
        if i == -1:
            return msg, ""
        return msg[:i], msg[i+1:]

    def get_params(self, user, cmd, msg):
        params = cmd_params()

        for arg in cmd.args:
            if len(msg) == 0:
                s = "Missing mandatory arguments."
                if self.irc.modules.get_module("help") != None:
                    s += " Use !help <command> to receive help on how to use the command."
                self.irc.priv_msg(user, s, 1)
                return None
            val, msg = commands.next_arg(msg)
            setattr(params, arg, val)

        for arg in cmd.optargs:
            val = None
            if len(msg) > 0:
                val, msg = commands.next_arg(msg)
            setattr(params, arg, val)

        return params
