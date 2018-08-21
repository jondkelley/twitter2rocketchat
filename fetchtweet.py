#from rocketchat.api import RocketChatAPI


"""Stalk a twitter user and post updates to a rocketchat channel
Usage:
    twitrocket [--twitter-handles HANDLES, --rocket-user USERNAME, --rocket-pass PASSWORD, --rocket-domain DOMAIN]

Arguments:
    HANDLES           a twitter handle to track
    USERNAME          rocket.chat username
    PASSWORD          rocket.chat password
    DOMAIN            rocket.chat domain

Options:
    -h                                       show this message
    -r, --twitter-handles HANDLES            a twitter handle to track
    -u, --rocket-user USERNAME               define a username
    -p, --rocket-pass PASSWORD               define a password
    -d, --rocket-domain DOMAIN               define a bot domain
"""

import codecs
import sys
import subprocess
import json
from time import sleep
from docopt import docopt
from rocketchat.api import RocketChatAPI

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

args = docopt(__doc__, options_first=True)
#
# api = RocketChatAPI(settings={'username': args['--rocket-user'], 'password': args['--rocket-pass'],
#                               'domain': args['--rocket-domain']})

ROOM = "GENERAL"
#api.send_message("it works!", ROOM)

def shell_command(command):
    """
    runs a command with subprocess
    returns a tuple (exitcode, stdout, stderr)
    """
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = p.communicate()
    exit_code = p.wait()
    return (exit_code, stdout, stderr)

class Index(object):
    """
    track previous tweets to prevent spamming a channel
    """
    def __init__(self, handle):
        self.twitterhandle = str(handle) # twitter handle
        self.index_name = "twitter-index.json"

    def exists(self, id):
        """
        returns true if a tweet exists in the index
        """
        index = self.load()
        if not self.twitterhandle in index:
            index[self.twitterhandle] = []
            self.save(index)
            return False
        elif id in index[self.twitterhandle]:
            return True
        else:
            return False

    def add(self, id):
        """
        adds a tweet id to the index
        """
        index = self.load()
        if id not in index[self.twitterhandle]:
            index[self.twitterhandle].append(id)
        self.save(index)

    def load(self):
        """
        loads the tweet index
        """
        try:
            with open(self.index_name) as f:
                return json.load(f)
        except:
            print("Error, db does not exist, resetting db")
            self.save({})
            return self.load()

    def save(self, data):
        """
        saves the index
        """
        with open(self.index_name, 'w') as outfile:
            json.dump(data, outfile)


def enhance(text):
    """
    doctor up the text
    """
    text = text.split(">")[1]
    text = text.replace("pic.twitter.com", " http://pic.twitter.com")
    return text

while True:
    """
    one infinite loop
    """

    twitter_handle = args['--twitter-handles']
    (e, stdout, stderr) = shell_command("php fetchtweet.php {}".format(twitter_handle))

    username = args['--rocket-user']
    print("Using user: {}".format(username))
    print("Using domain: {}".format(args['--rocket-domain']))
    print("Using pass: {}".format(args['--rocket-pass']))
    print("Using dom: {}".format(args['--rocket-domain']))
    api = RocketChatAPI(settings={'username': username, 'password': args['--rocket-pass'],
                                  'domain': args['--rocket-domain']})

    for tweet in json.loads(stdout)['tweets']:
        text = enhance(tweet['text'])
        id = tweet['date']

        tindex = Index(twitter_handle)
        if not tindex.exists(id):
            try:
                print("New message {} by {}: {}".format(id, twitter_handle, text))
            except:
                pass
            api.send_message(text, ROOM)
            tindex.add(id)
        else:
            print("Message {} by {} already indexed".format(id, twitter_handle))
    # sleep 15 minutes
    sleep(900)

