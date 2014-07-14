import commands, irc, irc_msg

uid_counter = 0

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
        self.hostmask = "" # same

        # set unique identifier
        global uid_counter
        uid_counter += 1
        self.uid = uid_counter

    def extract_hostname(self, prefix):
        if self.hostname == "":
            _, self.hostname = prefix.split("@", 1)

class irc_channel:
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
        for _, channel in self.channels.items():
            u = channel.user(nick)
            if u != None:
                return u
        return None

    def find_user_by_hostmask(self, hostmask):
        for _, channel in self.channels.items():
            for user in channel.users:
                if user.hostmask == hostmask:
                    return user
        return None

    def find_user_by_uid(self, uid):
        for _, channel in self.channels.items():
            for user in channel.users:
                if user.uid == uid:
                    return user
        return None

    def raw_msg(self, msg):
        if msg.cmd == "353":
            # add the channel if it's not yet in self.channels
            chan_name = msg.cmd_params[2]
            if chan_name not in self.channels:
                self.channels[chan_name] = irc_channel(chan_name)
            # add all listed users
            nicks = [msg.cmd_params[3]]
            if nicks[0].find(" ") != -1:
                nicks = nicks[0].split(" ")
            for nick in nicks:
                if len(nick) == 0:
                    continue
                user = self.find_user(nick)
                if user == None:
                    user = irc_user(nick)
                if user not in self.channels[chan_name].users:
                    self.channels[chan_name].users.append(user)
        elif msg.cmd == "PART":
            chan = msg.cmd_params[0]
            nick = msg.cmd_params[1]
            print(nick + " left " + chan + " (" + msg.cmd + ")")
            user = self.channels[chan].user(nick)
            self.channels[chan].users.remove(user)
            self.irc.modules.invoke('chan_quit', self.channels[chan], user, "leave")
            if self.find_user(nick) == None:
                self.irc.modules.invoke('user_gone', user)
        elif msg.cmd == "QUIT":
            nick, _ = msg.prefix.split("!", 1)
            for _, channel in self.channels.items():
                user = channel.user(nick)
                if user != None:
                    channel.users.remove(user)
                    self.irc.modules.invoke('chan_quit', channel, user, "quit")
            self.irc.modules.invoke('user_gone', user)
        elif msg.cmd == "JOIN":
            chan = msg.cmd_params[0]
            # add the channel if it's not yet in self.channels
            if chan not in self.channels:
                self.channels[chan] = irc_channel(chan)
            # create new user or get from other channels
            nick, _ = msg.prefix.split("!", 1)
            user = self.find_user(nick)
            if user == None:
                user = irc_user(nick)
            # add to this channel and invoke chan_join
            if user not in self.channels[chan].users:
                self.channels[chan].users.append(user)
                self.irc.modules.invoke('chan_join', self.channels[chan], user)
        elif msg.cmd == "MODE":
            self.handle_mode(msg)
        elif msg.cmd == "NICK":
            prev_nick, _ = msg.prefix.split("!", 1)
            new_nick = msg.cmd_params[0]
            user = self.find_user(nick)
            user.nick = nick
            # user.hostmask will be updated on next PRIVMSG
        elif msg.cmd == "PRIVMSG":
            if msg.cmd_params[0][0] == "#":
                chan = msg.cmd_params[0]
                nick, _ = msg.prefix.split("!", 1)
                user = self.channels[chan].user(nick)
                if user.hostmask != msg.prefix:
                    user.hostmask = msg.prefix
                user.extract_hostname(msg.prefix)
                self.irc.modules.invoke('chan_msg', self.channels[chan], user, msg.cmd_params[1])
                self.irc.commands.chan_msg(self.channels[chan], user, msg.cmd_params[1])

    def handle_mode(self, msg):
        print("todo")
