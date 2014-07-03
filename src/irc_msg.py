class irc_msg:
    def __init__(self):
        self.prefix = ""
        self.cmd = ""
        self.cmd_params = []

    def debug_print(self):
        print("prefix: " + self.prefix + ", cmd: " + self.cmd + ", params: " + str(self.cmd_params))
