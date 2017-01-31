#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import sys
import os.path
#import matplotlib.pyplot as pl
#import math as mt
#import spect_base_module as sbm
#import pickle
#import scipy.io as io
#import matplotlib.colors as colors
#import scipy.stats as stats
import spect_base_module as sbm
import twitter as tw
import json

# Functions to use in eloi_twit


def access(user=1):
    # Variables that contains the user credentials to access Twitter API
    keys = ['ACCESS_TOKEN', 'ACCESS_SECRET', 'CONSUMER_KEY', 'CONSUMER_SECRET']
    if user == 1:
        filename = '/home/fedefab/Scrivania/Idee/eloi_twit/access_tokens/user_1.acc'
        inputs = sbm.read_inputs(filename, keys, itype = 4*[str])
    elif user == 2:
        filename = '/home/fedefab/Scrivania/Idee/eloi_twit/access_tokens/user_2.acc'
        inputs = sbm.read_inputs(filename, keys, itype = 4*[str])
    else:
        print('User not valid')

    oauth = tw.OAuth(inputs['ACCESS_TOKEN'], inputs['ACCESS_SECRET'], inputs['CONSUMER_KEY'], inputs['CONSUMER_SECRET'])

    return oauth


def check_remaining_search(user = 1):
    # Checks how many requests are left for the Search API.

    oauth = access(user=user)
    twitter = tw.Twitter(auth=oauth)

    quantoresta = twitter.application.rate_limit_status(resources='search')
    restano = quantoresta['resources']['search']['/search/tweets']['remaining']
    print('Restano {} richieste\n'.format(restano))

    return restano


class my_tweet(object):
    """
    Simplified tweet object.
    """

    def __init__(self, tweet, internal_id = 0):
        print('dentro')
        self.int_id = internal_id
        self.tweet_id = tweet['id_str']
        self.user = tweet['user']['screen_name']
        self.user_id = tweet['user']['id_str']
        self.time = tweet['created_at']
        self.text = tweet['text']

        try:
            self.reply_to_user = tweet['in_reply_to_screen_name']
            self.reply_to_tweet_id_str = tweet['in_reply_to_status_id_str']
            self.flag_reply = True
        except:
            self.reply_to_user = None
            self.reply_to_tweet_id_str = None
            self.flag_reply = False

        try:
            rt = tweet['retweeted_status']
            self.retweeted_user = rt['user']['screen_name']
            self.retweeted_tweet_id = rt['id_str']
            self.flag_retweet = True
        except:
            self.flag_retweet = False
            self.retweeted_user = None
            self.retweeted_tweet_id = None

        try:
            qt = tweet['quoted_status']
            self.quoted_user = qt['user']['screen_name']
            self.quoted_tweet_id = tweet['quoted_status_id_str']
            self.flag_quote = True
        except:
            self.flag_quote = False
            self.quoted_tweet_id = None
            self.quoted_user = None

        hashtags = []
        for hashtag in tweet['entities']['hashtags']:
        	hashtags.append(hashtag['text'])
        self.hashtags = hashtags

        mentions = []
        for mention in tweet['entities']['user_mentions']:
        	mentions.append(mention['screen_name'])
        self.mentions = mentions

        self.link_to = [link(self.user,mention,link_type='mention') for mention in mentions]
        if self.flag_quote:
            self.link_to.append(link(self.user,quoted_user,link_type='quote'))
        if self.flag_retweet:
            self.link_to.append(link(self.user,retweeted_user,link_type='retweet'))
        if self.flag_reply:
            self.link_to.append(link(self.user,reply_to_user,link_type='reply'))

        return

    def other_method(self, *attr):
        print("Qui non c'è nulla!!\n")
        return

    def print_tw(self):
        print('{}: {} at {} --> {}\n'.format(self.int_id, r'@'+self.user, self.time, self.text.encode('utf-8')))
        return


class link(object):
    """
    Class to represent links (retweets, mentions, replies, quotes) between nodes (users) in the network.
    """
    def __init__(self,node1,node2,link_type='generic'):
        self.start = node1
        self.end = node2
        self.type = link_type
        return


class node(object):
    """
    Class to represent nodes (users) in the network.
    """
    def __init__(self, name = '', id_str = '', tweets_id = [], linked_to = []):
        self.name = name
        self.id_str = id_str
        self.tweets_id = tweets_id
        self.linked_to = linked_to
        self.tweets = 0
        self.mentions = 0
        self.retweeted = 0
        return

    def extract_from_tweet(self, tweet):
        self.name = tweet.user
        self.id_str = tweet.user_id
        self.tweets_id.append(tweet.tweet_id)
        self.linked_to = self.linked_to + tweet.link_to
        return


def read_json(filename, tweet_format = 'twitter'):
    """
    Reads json formatted file. Returns list of tweets in format of python dicts.
    :param tweet_format: if 'twitter' the output is a list of twitter.api.TwitterDictResponse, if 'my_tweet' my class is used
    """
    # We use the file saved from last step as example
    tweets_file = open(filename, "r")
    Tweets = []
    print('ciao!!')

    for line in tweets_file:
        #print(line)
        try:
            # Read in one line of the file, convert it into a json object
            tweet = json.loads(line.strip())
            print(type(tweet),tweet.keys())
            if 'text' in tweet: # only messages contains 'text' field is a tweet
                if tweet_format == 'twitter':
                    print(tweet['id_str'])
                    Tweets.append(tweet)
                elif tweet_format == 'my_tweet':
                    print('Entro')
                    print(tweet['id_str'])
                    zio = my_tweet(tweet)
                    print(type(zio))
                    print(tweet['user'])
                    print(zio.user)
                    Tweets.append(zio)
        except:
            # read in a line is not in JSON format (sometimes errors occur)
            continue

    return Tweets
