import socket

import mods, irc_msg

class irc:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.init_phase = True
        self.modules = mods.modules()

    def __del__(self):
        if hasattr(self, 'sock'):
            self.sock.close();

    def send(self, s):
        # cannot contain newlines or carriage-returns
        assert s.find("\n") == -1 and s.find("\r") == -1
        # run must've been called before send
        assert hasattr(self, 'sock')
        # max length of message
        assert len(s) <= 510

        print("sent: " + s)

        s += "\r\n"
        b = s.encode('utf-8')
        
        self.sock.sendall(b)

    def recv_loop(self):
        while True:
            bs = b""
            while True:
                bs += self.sock.recv(1)
                if bs.find(b"\r\n") != -1:
                    break

            bs = bs[:-2] # remove \r\n
            self.recv_handle(bs.decode('utf-8'))

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
       
        # XXX: pass message
        self.send("NICK tester")
        self.send("USER tester 0 * :Tester Jackson")

        self.recv_loop()

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
            self.send("PONG :" + str(msg.cmd_params[0]))

        if self.init_phase == True:
            if msg.cmd != "004" and msg.cmd != "PING":
                return
            self.init_phase = False
            # join channel
            self.send("JOIN #bot")
            # initialize all modules
            self.modules.invoke('init', self)

        # Initialization phase is finished, begin processing messages

        # pass raw message onto all active modules
        self.modules.invoke('raw_msg', msg)

