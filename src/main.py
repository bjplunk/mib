import argparse, socket

# Usage options
parser = argparse.ArgumentParser()
# Mandatory
parser.add_argument("server", help="server hostname to connect bot to")
parser.add_argument("nick", help="nickname of bot")
# Optional
parser.add_argument("-c", "--channel", help="join channels after connecting; multiple channels can be joined by providing a comma seperated list, such as: #a,#b,#c")
parser.add_argument("--rootpwd", help="set root password, if left empty no root account exists (requires auth module)")
args = parser.parse_args()

chans = []
rootpwd = ""
if args.channel:
    chans = [args.channel]
    if chans[0].find(",") != -1:
        chans = args.channel.split(",")
if args.rootpwd:
    rootpwd = args.rootpwd

# Handle args

import irc

i = irc.irc(args.server, args.nick, 6667, chans, rootpwd)
i.run()

