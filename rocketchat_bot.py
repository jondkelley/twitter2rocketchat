#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spawns a bot to post to twitter when feeds are updated
Usage:
    twitter_rocketchat_bot   --command [--config CONFIG_FILE]
Arguments:
    CONFIG_FILE          yaml configuration

Options:
    -h                                       show this message
    -c, --config CONFIG_FILE                 add a certain config file
"""
import codecs
import sys
import subprocess
import json
from time import sleep
from docopt import docopt
from rocketchat.api import RocketChatAPI
from twitteradapter import TwitterAdapter, TooManyRequestedTweets

#args = docopt(__doc__, options_first=True)

ROOM = "GENERAL"
#api.send_message("it works!", ROOM)

class JsonDb(object):
    """
    track previous tweets to prevent spamming a channel
    """
    def __init__(self, handle, dbname="twitter-index.json"):
        self.twitterhandle = str(handle) # twitter handle
        self.index_name = dbname

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

while True:
    """
    one infinite loop
    """

    handle = 'realdonaldtrump'
    twitter = TwitterAdapter(handle, 20)
    content = {}
    content['tweets'] = twitter.dict

    api = RocketChatAPI(settings={'username': 'xx', 'password': 'xx',
                                  'domain': 'xx'})

    for tweet in content['tweets']:
        text = tweet['text']
        id = tweet['tweetId']

        tindex = JsonDb(handle)
        if not tindex.exists(id):
            try:
                print("New message {} by {}: {}".format(id, handle, text))
            except:
                pass
            api.send_message(text, ROOM)
            tindex.add(id)
        else:
            print("Message {} by {} already indexed".format(id, handle))
    # sleep 15 minutes
    sleep(900)
