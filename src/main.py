import argparse, socket

# Usage options
parser = argparse.ArgumentParser()
# Mandatory
#parser.add_argument("server", help="server hostname to connect bot to")
#parser.add_argument("nick", help="nickname of bot")
# Optional
parser.add_argument("-c", "--channel", help="join channels after connecting; multiple channels can be joined by providing a comma seperated list, such as: #a,#b,#c")
args = parser.parse_args()

chans = []
if args.channel:
    chans = [args.channel]
    if chans[0].find(",") != -1:
        chans = args.channel.split(",")
    for chan in chans:
        print(chan)

# Handle args

import irc

i = irc.irc("127.0.0.1", 6667, chans)
i.run()

