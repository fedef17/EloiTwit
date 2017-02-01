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


def access_from_file(nomefile):
    """
    Returns oauth.
    File has to be in access_input.dat format and contain valid access tokens.
    """
    # Variables that contains the user credentials to access Twitter API
    keys = ['ACCESS_TOKEN', 'ACCESS_SECRET', 'CONSUMER_KEY', 'CONSUMER_SECRET']
    try:
        inputs = sbm.read_inputs(filename, keys, itype = 4*[str])
    except:
        raise ValueError('file not found!')

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


class EloiTweet(object):
    """
    Simplified tweet object.
    """

    def __init__(self, tweet, internal_id = 0):
        self.int_id = internal_id
        self.tweet_id = tweet['id']
        self.user = tweet['user']['screen_name']
        self.user_id = tweet['user']['id']
        self.time = tweet['created_at']
        self.text = tweet['text']
        self.retweet_count = tweet['retweet_count']
        self.favorite_count = tweet['favorite_count']



        #### MANCA ####
        # user followers e following e time zone
        # media e url del tweet



        if coordinates in tweet:
            self.loc_name = ''
            lat, lon = extract_json_coords(tweet['coordinates'])
            self.loc_coordinates = [lat,lon]
            self.loc_type = 'Tweet_GEO_ref'
        elif places in tweet:
            self.loc_name = tweet['places']['full_name']
            lat, lon = extract_json_coords(tweet['places']['bounding_box']['coordinates'])
            self.loc_coordinates = [lat,lon]
            self.loc_type = 'Tweet_GEO_tag'
        elif location in tweet['user']:
            self.loc_name = tweet['user']['location']
            lat, lon = find_coords_of_place(tweet['user']['location'])
            self.loc_coordinates = [lat, lon]
            self.loc_type = 'User_location'
        else:
            self.loc_coordinates = [np.nan, np.nan]
            self.loc_name = ''
            self.loc_type = None


        try:
            self.reply_to_user = tweet['in_reply_to_screen_name']
            self.reply_to_user_id = tweet['in_reply_to_user_id']
            self.reply_to_tweet_id = tweet['in_reply_to_status_id']
            self.flag_reply = True
        except:
            self.reply_to_user = None
            self.reply_to_user_id = None
            self.reply_to_tweet_id = None
            self.flag_reply = False

        try:
            rt = tweet['retweeted_status']
            self.retweeted_user = rt['user']['screen_name']
            self.retweeted_user_id = rt['user']['id']
            self.retweeted_tweet_id = rt['id']
            self.flag_retweet = True
        except:
            self.flag_retweet = False
            self.retweeted_user = None
            self.retweeted_user_id = None
            self.retweeted_tweet_id = None

        try:
            qt = tweet['quoted_status']
            self.quoted_user = qt['user']['screen_name']
            self.quoted_user_id = qt['user']['id']
            self.quoted_tweet_id = tweet['quoted_status_id_str']
            self.flag_quote = True
        except:
            self.flag_quote = False
            self.quoted_tweet_id = None
            self.quoted_user = None
            self.quoted_user_id = None

        hashtags = []
        for hashtag in tweet['entities']['hashtags']:
        	hashtags.append(hashtag['text'])
        self.hashtags = hashtags

        mention_ids = []
        mention_users = []
        for mention in tweet['entities']['user_mentions']:
            mention_users.append(mention['screen_name'])
            mention_ids.append(mention['id'])
        self.mention_users = mention_users
        self.mention_ids = mention_ids

        self.link_to = []
        for muser, mid in zip(mention_users, mention_ids):
            if self.flag_reply and mention == self.reply_to_user:
                linko = EloiLink(self.user_id,mid,link_type='reply')
            else:
                linko = EloiLink(self.user_id,mid,link_type='mention')
            self.link_to.append(linko)

        if self.flag_quote:
            linko = EloiLink(self.user_id,self.quoted_user_id,link_type='quote')
            self.link_to.append(linko)

        if self.flag_retweet:
            linko = EloiLink(self.user_id,self.retweeted_user_id,link_type='retweet')
            self.link_to.append(linko)

        return

    def other_method(self, *attr):
        print("Qui non c'è nulla!!\n")
        return

    def print_tw(self):
        print('{}: {} at {} --> {}\n'.format(self.int_id, r'@'+self.user, self.time, self.text.encode('utf-8')))
        return


class EloiLink(object):
    """
    Class to represent links (retweets, mentions, replies, quotes) between nodes (users) in the network.
    """
    def __init__(self,node1,node2,link_type='generic'):
        self.start = node1
        self.end = node2
        self.type = link_type
        return


class EloiNode(object):
    """
    Class to represent nodes (users) in the network.
    """
    def __init__(self, name = 'puppa!', user_id = None, tweets_id = [], links = []):
        self.name = name
        self.id = user_id
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


########################################################################
########################################################################
########################################################################

def find_coords_of_place(name):
    """
    Should work with some web help.. and if the name is real!
    """

    return np.nan, np.nan

def extract_json_coords(coordinates):
    """
    Extracts coordinates in json format and returns (lat,lon) of a point.
    ACHTUNG!! This reverts the order of (lat,lon) from JSON's (lon,lat).
    """
    if coordinates['type'] == 'Point':
        lat = coordinates['coordinates'][1]
        lon = coordinates['coordinates'][0]
    elif coordinates['type'] == 'Polygon':
        lat = np.mean(np.array([coordinates['coordinates'][0][i][1] for i in range(4)]))
        lon = np.mean(np.array([coordinates['coordinates'][0][i][0] for i in range(4)]))
    else:
        raise ValueError('coordinate type {} not recognized'.format(coordinates['type']))

    return lat, lon


def read_json(filename, tweet_format = 'twitter'):
    """
    Reads json formatted file. Returns list of tweets in format of python dicts.
    :param tweet_format: if 'twitter' the output is a list of twitter.api.TwitterDictResponse, if 'eloi' my class is used
    """
    # We use the file saved from last step as example
    tweets_file = open(filename, "r")
    Tweets = []
    print('ciao!!')

    #for line in tweets_file:
    for i in range(1):
        line = tweets_file.readline()
        #print(line)
        try:
            # Read in one line of the file, convert it into a json object
            tweet = json.loads(line.strip())
            print(type(tweet),tweet.keys())
            if 'text' in tweet: # only messages contains 'text' field is a tweet
                if tweet_format == 'twitter':
                    print(tweet['id_str'])
                    Tweets.append(tweet)
                elif tweet_format == 'eloi':
                    print('Entro')
                    print(tweet['id_str'])
                    zio = EloiTweet(tweet)
                    print(type(zio))
                    print(tweet['user'])
                    print(zio.user)
                    Tweets.append(zio)
                else:
                    raise ValueError('tweet_formats available: {}, {}'.format('twitter','eloi'))
        except:
            # read in a line is not in JSON format (sometimes errors occur)
            continue

    return Tweets
