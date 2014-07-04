import commands, irc, irc_msg

class irc_user:
    def __init__(self, irc_str):
        c = irc_str[0]
        # standard prefixes
        if c == "@" or c == "+":
            self.prefix = c
        # non-standard prefixes
        elif c == "~" or c == "&" or c == "%":
            self.prefix = c
        else:
            self.prefix = ""
        self.nick = irc_str[len(self.prefix):]
        self.hostname = "" # will be filled in on first PRIVMSG from user

    def extract_hostname(self, prefix):
        if self.hostname == "":
            _, self.hostname = prefix.split("@", 1)

class channel:
    def __init__(self, name):
        self.name = name
        self.users = []

    def user(self, nick):
        for u in self.users:
            if u.nick == nick:
                return u
        return None

class channels:
    def __init__(self, irc):
        self.irc = irc
        self.channels = {}

    # returns a user by nick from any of the channels we're in
    def find_user(self, nick):
        for chan in self.channels:
            u = chan.user(nick)
            if u != None:
                return u
        return None

    def raw_msg(self, msg):
        # NOTE
        # RFC1459 does not broadcast a JOIN on successful joins, we rely on RPL_NAMREPLY,
        # to signify a new channel. This would break if we start using the NAMES command

        if msg.cmd == "353":
            chan_name = msg.cmd_params[2]
            if chan_name not in self.channels:
                self.channels[chan_name] = channel(chan_name)
            users = [msg.cmd_params[3]]
            if users[0].find(" ") != -1:
                users = users[0].split(" ")
            for u in users:
                self.channels[chan_name].users.append(irc_user(u))
        elif msg.cmd == "PART" or msg.cmd == "QUIT":
            chan = msg.cmd_params[0]
            nick = msg.cmd_params[1]
            print(nick + " left " + chan + " (" + msg.cmd + ")")
            u = self.channels[chan].user(nick)
            self.channels[chan].users.remove(u)
            self.irc.modules.invoke('chan_quit', self.channels[chan], u, "leave" if msg.cmd == "PART" else "quit")
        elif msg.cmd == "JOIN":
            chan = msg.cmd_params[0]
            nick, _ = msg.prefix.split("!", 1)
            if nick == self.irc.nick:
                return # channel possibly not inserted yet if it's our JOIN message
            u = self.channels[chan].user(nick)
            if u == None:
                print(nick + " joined " + chan)
                u = irc_user(nick)
                self.channels[chan].users.append(u)
                self.irc.modules.invoke('chan_join', self.channels[chan], u)
        elif msg.cmd == "MODE":
            self.handle_mode(msg)
        elif msg.cmd == "NICK":
            prev_nick, _ = msg.prefix.split("!", 1)
            new_nick = msg.cmd_params[0]
            # replace name in all channels user is in
            for _, chan in self.channels.items():
                user = chan.user(prev_nick)
                if user == None:
                    continue
                print(user.nick + " in channel " + chan.name + " changed name to " + new_nick)
                chan.users.remove(user)
                user.nick = new_nick
                chan.users.append(user)
        elif msg.cmd == "PRIVMSG":
            if msg.cmd_params[0][0] == "#":
                chan = msg.cmd_params[0]
                nick, _ = msg.prefix.split("!", 1)
                u = self.channels[chan].user(nick)
                u.extract_hostname(msg.prefix)
                self.irc.modules.invoke('chan_msg', self.channels[chan], u, msg.cmd_params[1])
                self.irc.commands.chan_msg(self.channels[chan], u, msg.cmd_params[1])

    def handle_mode(self, msg):
        print("todo")
