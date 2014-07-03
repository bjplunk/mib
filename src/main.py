import argparse, socket

# Usage options
#parser = argparse.ArgumentParser()
# Mandatory
#parser.add_argument("server", help="server hostname to connect bot to")
#parser.add_argument("nick", help="nickname of bot")
# Optional
#parser.add_argument("-c", "--channel", help="join channel after connecting")
#args = parser.parse_args()

# Handle args

import irc

i = irc.irc("127.0.0.1", 6667)
i.run()

