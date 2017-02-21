#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import sys
import os.path
import matplotlib.pyplot as pl
import math as mt
import matplotlib.colors as colors
import scipy.stats as stats
import warnings

import twitter as tw
import json
import socket
import time
import urllib
import urllib2
import argparse

# Functions to use in eloi_twit


def prova_ciclo():
    for i in range(10):
        if i > 3:
            print(i)
            if i > 7:
                break
            if i > 5:
                continue
            if i > 7:
                break
            print('ciao')
    return


def access(user=1):
    # Variables that contains the user credentials to access Twitter API
    keys = ['ACCESS_TOKEN', 'ACCESS_SECRET', 'CONSUMER_KEY', 'CONSUMER_SECRET']
    if user == 1:
        filename = '/home/fedefab/Scrivania/Idee/eloi_twit/access_tokens/user_1.acc'
        inputs = read_inputs(filename, keys, itype = 4*[str])
    elif user == 2:
        filename = '/home/fedefab/Scrivania/Idee/eloi_twit/access_tokens/user_2.acc'
        inputs = read_inputs(filename, keys, itype = 4*[str])
    else:
        print('User not valid')

    oauth = tw.OAuth(inputs['ACCESS_TOKEN'], inputs['ACCESS_SECRET'], inputs['CONSUMER_KEY'], inputs['CONSUMER_SECRET'])

    return oauth


def parseArguments(program):
    """
    Creates argument parser for code inputs.
    """
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument("input_file", help="input_file", type=str)

    # Optional arguments
    parser.add_argument("-ll", "--live", help="Std Output", type=bool, default=False)
    parser.add_argument("--log", help="log file", type=str, default='log_eloi_'+program+'.log')
    parser.add_argument("-v", "--verbose", help="Verbose", type=bool, default=False)

    # Parse arguments
    args = parser.parse_args()

    return args


def wait_requests(twitter, num_min = 180, n_trials = 10, sleep_time = 0, wait = False, interval = 30):
    """
    twitter is a twitter API.
    Waits until at least 'num' requests are available or there is connection. Makes 'n_trials' requests waiting 30s in between. If sleep_time is set, waits the sleep_time before.
    If wait is True, waits until the num_min is reached, if trials < n_trials.
    Returns: ok_bool, restano
    """
    if sleep_time > 0:
        print('Waiting {} seconds.\n'.format(sleep_time))
        time.sleep(sleep_time)

    restano = None
    ok_bool = False
    Connected = internet_on()
    if not Connected:
        wait_connection()

    quantoresta_rate_limit = twitter.application.rate_limit_status(resources='application')
    resta = quantoresta_rate_limit['resources']['application']['/application/rate_limit_status']['remaining']
    if resta < n_trials + 1:
        print('Not enough requests to see if there are enough requests!!\n')
        return ok_bool, restano, NoConnection

    done = False
    trials = 0
    while not done and trials <= n_trials:
        trials+=1
        try:
            quantoresta = twitter.application.rate_limit_status(resources='search')
            restano = quantoresta['resources']['search']['/search/tweets']['remaining']
            print('Restano {} richieste\n'.format(restano))
            if not wait:
                done = True
            else:
                if restano >= num_min:
                    done = True
                else:
                    time.sleep(interval)
        except:
            Connected = internet_on()
            if not Connected: print('No Internet connection, trial {}\n'.format(trials))
            time.sleep(30)

    if done:
        ok_bool = True

    return ok_bool, restano


def wait_connection(sleep_time = 30):
    """
    Waits till internet connection is ON.
    Returns True when finished.
    Improve: Send a Notification when no connection is found for more than a chosen interval.
    """
    time0 = time.ctime()
    Connected = internet_on()
    while not Connected:
        print('NO INTERNET CONNECTION since {}\n'.format(time0))
        Connected = internet_on()
        time.sleep(sleep_time)

    return Connected


def PrintEmptyLine(ofile = None, num = 1):
    if ofile is None:
        for i in range(num):
            print('\n')
    else:
        for i in range(num):
            ofile.write('\n')
    return


def PrintBreakLine(ofile = None, num = 1, length = 100, plus_empty = False, strong = False):
    string = length*'-'
    string2 = length*'/'
    if plus_empty: string+='\n'

    if ofile is None:
        for i in range(num):
            print(string)
            if strong: print(string2)
    else:
        for i in range(num):
            ofile.write(string)
            if strong: ofile.write(string2)
    return


def PrintEmph(string, ofile = None, level = 1):
    strong = False
    if level > 1: strong = True
    PrintEmptyLine(ofile = ofile)
    PrintBreakLine(num = level, ofile = ofile, strong = strong)
    if level == 2: PrintEmptyLine(ofile = ofile)

    if ofile is None:
        print(string)
    else:
        ofile.write(string)

    if level == 2: PrintEmptyLine(ofile = ofile)
    PrintBreakLine(num = level, ofile = ofile, strong = strong)
    PrintEmptyLine(ofile = ofile)

    return

def access_from_file(filename):
    """
    Returns oauth.
    File has to be in access_input.dat format and contain valid access tokens.
    """
    # Variables that contains the user credentials to access Twitter API
    keys = ['ACCESS_TOKEN', 'ACCESS_SECRET', 'CONSUMER_KEY', 'CONSUMER_SECRET']
    try:
        inputs = read_inputs(filename, keys, itype = 4*[str])
    except:
        raise ValueError('file not found!')

    oauth = tw.OAuth(inputs['ACCESS_TOKEN'], inputs['ACCESS_SECRET'], inputs['CONSUMER_KEY'], inputs['CONSUMER_SECRET'])

    return oauth


def internet_on(host="8.8.8.8", port=53, timeout=3):
    """
    Thanks to 7h3rAm on stackoverflow.
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print(ex.message)
        print("I don't know whether port 53 is valid for everywhere in the world.. If this problem appears again, try commenting out the lines that involve this routine, which is simply a check of the internet connection.")
        return False


def read_inputs(nomefile, key_strings, n_lines = None, itype = None, defaults = None, verbose=False):
    """
    Standard reading for input files. Searches for the keys in the input file and assigns the value to variable.
    :param keys: List of strings to be searched in the input file.
    :param defaults: List of default values for the variables.
    :param n_lines: List. Number of lines to be read after key.
    """

    keys = ['['+key+']' for key in key_strings]

    if n_lines is None:
        n_lines = np.ones(len(keys))

    if itype is None:
        itype = len(keys)*[None]

    if defaults is None:
        #warnings.warn('No defaults are set. Setting None as default value.')
        defaults = len(keys)*[None]

    variables = []
    is_defaults = []
    with open(nomefile, 'r') as infile:
        lines = infile.readlines()
        # Skips commented lines:
        lines = [line for line in lines if not (line.lstrip()[0:2] == '#[' or line.lstrip()[0:2] == '# ')]

        for key, deflt, nli, typ in zip(keys,defaults,n_lines,itype):

            is_key = np.array([key in line for line in lines])
            if np.sum(is_key) == 0:
                print('Key {} not found, setting default value {}'.format(key,deflt))
                variables.append(deflt)
                is_defaults.append(True)
            elif np.sum(is_key) > 1:
                raise KeyError('Key {} appears {} times, should appear only once.'.format(key,np.sum(is_key)))
            else:
                num_0 = np.argwhere(is_key)[0][0]
                if nli == 1:
                    cose = lines[num_0+1].split()
                    if typ == bool: cose = [str_to_bool(lines[num_0+1].split()[0])]
                    if typ == str: cose = [lines[num_0+1].rstrip()]
                    if len(cose) == 1:
                        variables.append(map(typ,cose)[0])
                    else:
                        variables.append(map(typ,cose))
                else:
                    cose = []
                    for li in range(nli):
                        cos = lines[num_0+1+li].split()
                        if typ == str: cos = [lines[num_0+1+li].rstrip()]
                        if len(cos) == 1:
                            cose.append(map(typ,cos)[0])
                        else:
                            cose.append(map(typ,cos))
                    variables.append(cose)
                is_defaults.append(False)

    if verbose:
        for key, var, deflt in zip(keys,variables,is_defaults):
            print('----------------------------------------------\n')
            if deflt:
                print('Key: {} ---> Default Value: {}'.format(key,var))
            else:
                print('Key: {} ---> Value Read: {}'.format(key,var))

    return dict(zip(key_strings,variables))


def check_remaining_search(user = None, access_file = None):
    """
    Checks how many requests are left for the Search API.
    """
    if user is None and access_file is None:
        raise ValueError('No access_tokens given\n')
    elif user is not None:
        oauth = access(user=user)
    elif access_file is not None:
        oauth = access_from_file(access_file)

    twitter = tw.Twitter(auth=oauth)

    quantoresta = twitter.application.rate_limit_status(resources='search')
    restano = quantoresta['resources']['search']['/search/tweets']['remaining']
    print('Restano {} richieste\n'.format(restano))

    return restano


######### Classes!! #######################


class EloiNetwork(object):
    """
    Network object. Contains Nodes and Links. Contains subnets, which are same type objects.
    """
    def __init__(self, nodes, links):
        pass



class EloiTweet(object):
    """
    Simplified tweet object.
    """

    def __init__(self, tweet, internal_id = 0):
        self.int_id = internal_id
        self.tweet_id = tweet['id']
        self.user_name = tweet['user']['screen_name']
        self.user_id = tweet['user']['id']
        self.time = tweet['created_at']
        self.text = tweet['text']
        self.retweet_count = tweet['retweet_count']
        self.favorite_count = tweet['favorite_count']

        self.user = tweet['user']['screen_name']
        self.user_descr = tweet['user']['description']
        self.user_followers = tweet['user']['followers_count']
        self.user_following = tweet['user']['friends_count']
        self.user_geo_enabled = tweet['user']['geo_enabled']
        self.user_location = tweet['user']['location']
        self.user_tw_count = tweet['user']['statuses_count']
        self.user_timezone = tweet['user']['time_zone']

        self.media_type = []
        self.media_url = []
        try:
            for media in tweet['entities']['media']:
                self.media_type.append(media['type'])
                self.media_url.append(media['media_url'])
        except Exception as cazzillo:
            pass
            #print('Found exception: {} -> {}'.format(type(cazzillo),cazzillo))

        self.url_links = []
        try:
            for url in tweet['entities']['urls']:
                self.url_links.append(url['display_url'])
        except Exception as cazzillo:
            pass
            #print('Found exception: {} -> {}'.format(type(cazzillo),cazzillo))

        if tweet['coordinates'] is not None:
            self.loc_name = ''
            print('coords',tweet['coordinates'])
            lat, lon = extract_json_coords(tweet['coordinates'])
            self.loc_coordinates = [lat,lon]
            self.loc_type = 'Tweet_GEO_ref'
        elif tweet['place'] is not None:
            print('place',tweet['place'])
            self.loc_name = tweet['place']['full_name']
            lat, lon = extract_json_coords(tweet['place']['bounding_box'])
            self.loc_coordinates = [lat,lon]
            self.loc_type = 'Tweet_GEO_tag'
        elif tweet['user']['location'] != '':
            print('userloc',tweet['user']['location'])
            self.loc_name = tweet['user']['location']
            lat, lon = find_coords_of_place(tweet['user']['location'])
            self.loc_coordinates = [lat, lon]
            self.loc_type = 'User_location'
        else:
            print('NO COORDS')
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
        try:
            for hashtag in tweet['entities']['hashtags']:
        	       hashtags.append(hashtag['text'])
        except Exception as cazzillo:
            print('Found exception: {}'.format(cazzillo))
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
        self.id_A = node1
        self.id_B = node2
        self.type = link_type
        self.node_A = None
        self.node_B = None
        return

    def add_node_objects(self,node1,node2):
        """
        Creates two attributes with EloiNode type starting and ending nodes.
        """
        if type(node1) or type(node2) is not EloiNode:
            raise ValueError('not an EloiNode object')

        self.node_A = node1
        self.node_B = node2

        return


class EloiLinkSum(object):
    """
    Class to represent the sum of the links between two nodes.
    link_list is a list of EloiLink objects that connect two nodes.
    """
    def __init__(self, link_list):
        node1 = link_test[0].node_A
        node2 = link_test[0].node_B
        num1 = len([nod for nod in link_list if nod.node_A == node1])
        num2 = len([nod for nod in link_list if nod.node_A == node2])
        if num1 >= num2:
            self.node_A = node1
            self.node_B = node2
            self.total_AB = num1
            self.total_BA = num2
        else:
            self.node_A = node2
            self.node_B = node1
            self.total_AB = num2
            self.total_BA = num1

        self.total = len(link_list)
        self.links = link_list

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

    for line in tweets_file:
        try:
            # Read in one line of the file, convert it into a json object
            tweet = json.loads(line.strip())

            if 'text' in tweet: # only messages contains 'text' field is a tweet
                if tweet_format == 'twitter':
                    Tweets.append(tweet)
                elif tweet_format == 'eloi':
                    zio = EloiTweet(tweet)
                    Tweets.append(zio)
                else:
                    raise ValueError('tweet_formats available: {}, {}'.format('twitter','eloi'))
        except Exception as ciccio:
            print('An error occurred: {}. Just skipping..'.format(ciccio))
            raise
            # read in a line is not in JSON format (sometimes errors occur)
            continue

    return Tweets
