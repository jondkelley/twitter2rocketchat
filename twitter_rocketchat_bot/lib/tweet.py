#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import islice
from json import dumps
from operator import itemgetter
import datetime
from twitter_scraper import get_tweets

class TooManyRequestedTweets(Exception):
    """
    gets raised when more then 40 tweets, the limit per page!
    """
    pass

class TwitterAdapter(object):
    """
    simple adapter class to utilize twitter_scraper and pull out tweets in various forms
    """
    def __init__(self, handle, num_items=40, reverse=True):
        self.version = 1
        if num_items > 40:
            raise TooManyRequestedTweets("Can't specify more then 40 tweets")
        self.handle = handle
        self.num_items = num_items
        self.reverse = reverse
        self.raw = self.retrieve()

    def transform_tweet(self, tweetitem):
        """
        performs useful transformations on tweet properties
        """
        for k, v in tweetitem.items():
            if k == "text":
                # replace pic url with secure pic url
                v = v.replace("\u00a0pic.twitter.com", " https://pic.twitter.com")
            tweetitem[k] = v

        # rename time as timeEpoch
        # convert items to integers
        tweetitem['timeEpoch'] = int(tweetitem['time'])
        tweetitem['tweetId'] = int(tweetitem['tweetId'])
        tweetitem['textLength'] = len(tweetitem['text'])
        return tweetitem

    def retrieve(self):
        """
        retrieves a block of up to 40 tweets
        """
        tweets = []
        tfeed = get_tweets(self.handle, pages=1)
        for tweet in tfeed:
            tweetitem = {}
            for k, v in tweet.items():
                if k == "time":
                    # convert dt to epoch
                    v = v.strftime('%s')
                tweetitem[k] = v
            # common transforms
            tweetitem = self.transform_tweet(tweetitem)
            # convert time field to datetime
            tweetitem['time'] = datetime.datetime.fromtimestamp(tweetitem['timeEpoch']).strftime('%Y-%m-%d %H:%M:%S')
            tweetitem['entries'] = {}
            # copy over sub-entries
            tweetitem['entries']['hashtags'] = tweet['entries']['hashtags']
            tweetitem['entries']['urls'] = tweet['entries']['urls']
            tweetitem['entries']['photos'] = tweet['entries']['photos']
            tweetitem['entries']['videos'] = tweet['entries']['videos']
            tweets.append(tweetitem)

        # sort list by epoch newest first
        tweets = sorted(tweets, key=itemgetter('time'), reverse=self.reverse)
        # restrict list to first length of self.num_items
        tweets = [k for k in islice(tweets, self.num_items)]
        # append incremental stackId to list of tweets
        for x in tweets:
            i = tweets.index(x)
            tweets[i]['stackId'] = i + 1
        return tweets

    @property
    def dict(self):
        """
        returns twitter stream as dictionary
        """
        return self.raw

    @property
    def json(self):
        """
        returns twitter stream as json
        """
        return dumps(self.raw, indent=2)

    @property
    def latest(self):
        """
        returns twitter stream last tweet
        """
        return self.raw[0]
