import time, socket

import commands, channels, mods, irc_msg

class irc:
    def __init__(self, host, port, chans):
        self.host = host
        self.port = port
        self.nick = "tester"
        self.command_char = "!"
        self.init_phase = True
        self.auto_join = chans

        # core functionality (available for all modules)
        self.channels = channels.channels(self)
        self.commands = commands.commands(self)
        self.modules = mods.modules(self) # need to be constructed last of the core modules

        # queues have the same outgoing interval, that critical_queue remains
        # more responsive is up to module writers staying reponsible
        self.critical_queue = []
        self.noncritical_queue = []
        self.shitter_queue = [] # for spammers
        self.crit_time = 0
        self.ncrit_time = 0
        self.shitter_time = 0
        self.user_sent = {}
        self.user_time = 0 # clear user_sent every X time period
        self.blacklisted = {}

    def __del__(self):
        if hasattr(self, 'sock'):
            self.sock.close();

    def chan_msg(self, channel, msg, queue=2, user=None):
        s = "PRIVMSG " + channel.name + " :" + msg
        self.send(s, queue, user)

    def priv_msg(self, user, msg, queue=2):
        s = "PRIVMSG " + user.nick + " :" + msg
        self.send(s, queue, user)

    # queue: 0: instant, 1: critical messages, 2: non-critical messages, else: spammer queue (size limited)
    # user: user that is the reason we are sending this message, if applicable => enables the spam limit
    def send(self, s, queue=2, user=None):
        # cannot contain newlines or carriage-returns
        assert s.find("\n") == -1 and s.find("\r") == -1
        # run must've been called before send
        assert hasattr(self, 'sock')
        # max length of message
        assert len(s) <= 510

        s += "\r\n"
        b = s.encode('utf-8')

        if user != None:
            if not user.hostname in self.user_sent:
                self.user_sent[user.hostname] = 0
            self.user_sent[user.hostname] += 1

            # if a user gets into blacklisted he needs to wait a full minute before he starts invoking commands
            if user.hostname in self.blacklisted:
                print(user.nick + "'s visit in the shitter queue extended to a full minute")
                self.blacklisted[user.hostname] = time.time()
                queue = 3
            elif self.user_sent[user.hostname] >= 20:
                print("added " + user.nick + " to shitter queue")
                self.blacklisted[user.hostname] = time.time()
                queue = 3
        
        if queue == 0:
            self.sock.sendall(b)
        elif queue == 1:
            self.critical_queue.append(b)
        elif queue == 2:
            self.noncritical_queue.append(b)
        else:
            if len(self.shitter_queue) < 4096:
                self.shitter_queue.append(b)

    def net_loop(self):
        self.sock.settimeout(0.2)
        bs = b""
        while True:
            while True:
                try:
                    bs += self.sock.recv(1)
                except socket.timeout:
                    break
                if bs.find(b"\r\n") != -1:
                    break
            
            # process message if a full message has been received
            if bs.find(b"\r\n") != -1:
                bs = bs[:-2] # remove \r\n
                self.recv_handle(bs.decode('utf-8'))
                bs = b""

            # handle sending of queues
            self.send_queues()

    def send_queues(self):
        # clear user_time
        if self.user_time+60.0 <= time.time():
            self.user_sent.clear()
            self.user_time = time.time()
        # trim blacklisted
        del_keys = []
        for k,v in self.blacklisted.items():
            if v+60.0 < time.time():
                del_keys.append(k)
        for k in del_keys:
            del self.blacklisted[k]

        if len(self.critical_queue) > 0 and time.time() >= self.crit_time + 1.0:
            self.sock.send(self.critical_queue[0], 0)
            self.critical_queue = self.critical_queue[1:]
            self.crit_time = time.time()
        if len(self.noncritical_queue) > 0 and time.time() >= self.ncrit_time + 2.0:
            self.sock.send(self.noncritical_queue[0], 0)
            self.noncritical_queue = self.noncritical_queue[1:]
            self.ncrit_time = time.time()
        # only send from shitter_queue once the other queues are depleted
        if len(self.critical_queue) != 0 or len(self.noncritical_queue) != 0:
            return
        if len(self.shitter_queue) > 0 and time.time() >= self.shitter_time + 2.0:
            self.sock.send(self.shitter_queue[0], 0)
            self.shitter_queue = self.shitter_queue[1:]
            self.shitter_time = time.time()

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
       
        # XXX: pass message
        self.send("NICK tester", 0)
        self.send("USER tester 0 * :Tester Jackson", 0)

        self.net_loop()

    # handles raw input
    def recv_handle(self, s):
        msg = irc_msg.irc_msg()
        index = 0

        # extract optional prefix
        if s[index] == ":":
            index += 1
            old_index = index
            index = s.find(" ", index)
            msg.prefix = s[old_index:index]
            index += 1

        # extract command
        old_index = index
        index = s.find(" ", index)
        msg.cmd = s[old_index:index]
        index += 1

        # extract command parameters
        while index < len(s) and s[index] != ":":
            old_index = index
            index = s.find(" ", index)
            if index == -1:
                index = len(s)
            msg.cmd_params.append(s[old_index:index])
            index += 1

        # extract trailing command parameter
        if index < len(s) and s[index] == ":":
            msg.cmd_params.append(s[index+1:len(s)])

        self.msg_handle(msg)

    # handles parsed irc messages
    def msg_handle(self, msg):
        # some irc server software send PING as the first message (which seems to be contrary to RFC2812)
        if msg.cmd == "PING":
            self.send("PONG :" + str(msg.cmd_params[0]), 0)

        if self.init_phase == True:
            if msg.cmd != "004" and msg.cmd != "PING":
                return
            self.init_phase = False
            # join auto-join channels
            for chan in self.auto_join:
                self.send("JOIN " + chan)

        # Initialization phase is finished, begin processing messages

        # pass raw message to core modules
        self.channels.raw_msg(msg)

        # pass raw message onto all active modules
        self.modules.invoke('raw_msg', msg)

        # user to user private messages
        if msg.cmd == "PRIVMSG" and msg.cmd_params[0][0] != "#" and msg.cmd_params[0][0] != "&":
            # only handle private user to user messages if the user is in a channel we are in as well
            nick = msg.cmd_params[0][1:]
            user = self.channels.find_user(nick)
            if user != None:
                message = msg.cmd_params[1]
                self.commands.priv_msg(user, message)
                self.modules.invoke('priv_msg', user, message)

