#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from rocketchat.api import RocketChatAPI
from time import sleep
from twitter_rocketchat_bot.lib.tweet import (TwitterAdapter, TooManyRequestedTweets)
import yaml
import logging
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('twitter_rocketchat_bot')
logger.setLevel(logging.DEBUG)
class JsonRemembers(object):
    """
    track previous tweets to prevent spamming a channel
    """
    def __init__(self, handle, dbname="/opt/twitter_rocketchat_bot.index"):
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
            logger.info("Error, db does not exist, resetting db")
            self.save({})
            return self.load()

    def save(self, data):
        """
        saves the index
        """
        with open(self.index_name, 'w') as outfile:
            json.dump(data, outfile)

class BadConfigFile(Exception):
    """
    raise when the configuration is not parsable
    """
    pass

class Configuration(object):
    """
    parse yaml config
    """
    def __init__(self, config=None):
        filename = 'twitter_rocketchat_bot.conf'
        with open(filename) as f:
            self.config = yaml.load(f)
        self.validate()

    def validate(self):
        """
        validates configuration format as best as we can
        """
        # read_interval
        try:
            self.config['read_interval']
        except:
            raise BadConfigFile("{}: missing value read_interval".format(filename))
            exit(1)
        if type(self.config['read_interval']) is not int:
            raise BadConfigFile("{}: read_interval must be int()".format(filename))
            exit(1)
        # at least 1 server
        # at least 1 room
        # at least 1 account
        # validate all id fields are integers
        # server
        # room
        # account

    @property
    def interval(self):
        """
        return list of twitter handles
        """
        return self.config['read_interval']

    @property
    def twitter_handles(self):
        """
        return list of twitter handles
        """
        handles = []
        for handle in self.config['twitter_watch']:
            handles.append(handle['handle'])
        return handles

    def get_rooms(self, hindex):
        """
        return list of room names for handle
        """
        roomids = self.config['twitter_watch'][hindex]['roomId']
        if type(roomids) is list:
            pass
        else:
            roomids = roomids.split(',')
        rooms = []
        for roomid in roomids:
            room = self.config['rooms'][roomid]['name']
            rooms.append(room)
        return rooms

    def get_server(self, hindex):
        """
        return list of servers for handle
        """
        serverid = self.config['twitter_watch'][hindex]['serverId']
        return self.config['servers'][serverid]['url']

    def get_account(self, hindex):
        """
        return list of account creds for handle
        """
        accountid = int(self.config['twitter_watch'][hindex]['accountId'])
        return (self.config['accounts'][accountid]['user'], self.config['accounts'][accountid]['pass'])

def transform(tweet):
    """
    change a tweet text post process
    """
    tweet = tweet.replace("pic.twitter.com", " https://pic.twitter.com")
    return tweet

def loop():
    """
    trigger loop
    """
    while True:
        """
        one infinite loop
        """
        conf = Configuration()
        for handle in conf.twitter_handles:
            hindex = conf.twitter_handles.index(handle)
            username, password = conf.get_account(hindex)
            url = conf.get_server(hindex)
            chat = RocketChatAPI(
                settings={
                    'username': username,
                    'password': password,
                    'domain': url
                    }
                )

            twits = TwitterAdapter(handle, 10)
            twit_feed = twits.dict
            for tweet in twit_feed:
                text = tweet['text']
                id = tweet['tweetId']

                jindex = JsonRemembers(handle)
                if not jindex.exists(id):
                    logger.info("id {} by {} sent".format(id, handle))
                    for channel in conf.get_rooms(hindex):
                        try:
                            text = transform(text)
                            chat.send_message(text, channel)
                        except json.decoder.JSONDecodeError:
                            logger.info("Could not read server response, bad server url?")
                    jindex.add(id)
                else:
                    logger.info("id {} by {} already sent".format(id, handle))

        logger.info("Sleeping {} seconds".format(conf.interval * 60))
        sleep(conf.interval * 60)

if __name__ == '__main__':
    loop()
