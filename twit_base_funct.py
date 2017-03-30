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
    def __init__(self, name, nodes = None, links = None, linksums = None, tweets = None):
        self.nodes = nodes
        self.edges = linksums
        self.all_links = links
        self.name = name
        self.tweets = tweets
        return

    def create_from_cart(self, cart):
        """
        Reads all tweets in cart and builds the EloiNetwork object.
        """
        tweets = load_stream(cart, tag = None)
        self.create_from_tweets_list(tweets)
        return

    def create_from_tweets_list(self, tweets):
        """
        Produces an EloiNetwork object with nodes and edges directly from the list of tweets.
        """

        self.tweets = tweets
        print(len(tweets))

        tweet_user_ids = np.array([twe.user_id for twe in tweets])
        node_ids = np.unique(tweet_user_ids)
        print(len(node_ids))

        nodes = []
        for nid in node_ids:
            tweets_lui = [twe for twe in tweets if twe.user_id == nid]
            nodo = EloiNode(tweets = tweets_lui)
            nodes.append(nodo)

        links = []
        for twe in tweets:
            links += [lin for lin in twe.link_to]

        edges = []
        for nodo in nodes:
            link_to_nodo = [lin for lin in links if lin.id_B == nodo.id]
            nodo.complete_interactions(link_to_nodo)
            nodo.sum_links()
            edges += nodo.sum_point_to

        self.nodes = nodes
        self.edges = edges
        self.all_links = links

        return


    def geo_map(self):
        pass

    def network_map(self):
        pass

    def show_node_list(self):
        pass

    def show_edges_list(self):
        pass

    def export_node_csv(self, filename = None):
        if filename is None:
            filename = self.name + '_nodes.csv'
        export_node_csv(self, filename)
        return

    def export_edges_csv(self, filename = None):
        if filename is None:
            filename = self.name + '_edges.csv'
        export_edges_csv(self, filename)
        return



class EloiTweet(object):
    """
    Simplified tweet object.
    """

    def __init__(self, tweet, internal_id = 0):
        self.int_id = internal_id
        self.id = tweet['id']
        self.user_name = tweet['user']['screen_name']
        self.user_id = tweet['user']['id']
        self.created_at = tweet['created_at']
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
        self.lang = tweet['lang']

        self.media_type = []
        self.media_url = []
        try:
            for media in tweet['entities']['media']:
                self.media_type.append(media['type'])
                self.media_url.append(media['media_url'])
                raise EnvironmentError('MANCANO LE TAGS!! devi estrarle')
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
            #print('coords',tweet['coordinates'])
            lat, lon = extract_json_coords(tweet['coordinates'])
            self.loc_coordinates = [lat,lon]
            self.loc_type = 'Tweet_GEO_ref'
        elif tweet['place'] is not None:
            #print('place',tweet['place'])
            self.loc_name = tweet['place']['full_name']
            lat, lon = extract_json_coords(tweet['place']['bounding_box'])
            self.loc_coordinates = [lat,lon]
            self.loc_type = 'Tweet_GEO_tag'
        elif tweet['user']['location'] != '':
            #print('userloc',tweet['user']['location'])
            self.loc_name = tweet['user']['location']
            lat, lon = find_coords_of_place(tweet['user']['location'])
            self.loc_coordinates = [lat, lon]
            self.loc_type = 'User_location'
        else:
            #print('NO COORDS')
            self.loc_coordinates = [np.nan, np.nan]
            self.loc_name = ''
            self.loc_type = None

        self.type = 'Tweet'

        try:
            self.reply_to_user = tweet['in_reply_to_screen_name']
            self.reply_to_user_id = tweet['in_reply_to_user_id']
            self.reply_to_tweet_id = tweet['in_reply_to_status_id']
            self.flag_reply = True
            self.type = 'Reply'
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
            self.type = 'Retweet'
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
            self.type = 'Quote'
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
            if self.flag_reply and muser == self.reply_to_user:
                linko = EloiLink(self.user_id,mid,self.user_name,muser,self.id,self.created_at,link_type='Reply')
            else:
                linko = EloiLink(self.user_id,mid,self.user_name,muser,self.id,self.created_at,link_type='Mention')
            self.link_to.append(linko)

        if self.flag_quote:
            linko = EloiLink(self.user_id,self.quoted_user_id,self.user_name,self.quoted_user,self.id,self.created_at,link_type='Quote')
            self.link_to.append(linko)

        if self.flag_retweet:
            linko = EloiLink(self.user_id,self.retweeted_user_id,self.user_name,self.retweeted_user,self.id,self.created_at,link_type='Retweet')
            self.link_to.append(linko)

        return

    def other_method(self, *attr):
        print("Qui non c'è nulla!!\n")
        return

    def print_tw(self):
        print('{}: {} at {} --> {}\n'.format(self.id, r'@'+self.user, self.created_at, self.text.encode('utf-8')))
        return


class EloiLink(object):
    """
    Class to represent links (retweets, mentions, replies, quotes) between nodes (users) in the network. Uniquely linked to a tweet.
    """
    def __init__(self,node1,node2,node1_name,node2_name,tweet_id,created_at,link_type=None):
        self.id_A = node1
        self.id_B = node2
        self.name_A = node1_name
        self.name_B = node2_name
        self.type = link_type
        self.tweet_id = tweet_id
        self.created_at = created_at
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
    Class to represent the sum of the links between two nodes, with a determined direction. So, this is a vector: intensity (weight), direction (AB) and verse (A to B) are specified.
    link_list is a list of EloiLink objects that connect two nodes.
    """
    def __init__(self, link_list, node_id_A):
        self.id_A = node_id_A
        self.id_B = link_list[0].id_B
        self.name_A = link_list[0].name_A
        self.name_B = link_list[0].name_B
        if self.id_B == self.id_A:
            self.id_B = link_list[0].id_A
            self.name_A = link_list[0].name_B
            self.name_B = link_list[0].name_A

        num1 = len([link for link in link_list if link.id_A == node_id_A])

        self.weight = num1
        self.links = [link for link in link_list if link.id_A == node_id_A]
        self.timeset = [link.created_at for link in link_list if link.id_A == node_id_A]

        return


class EloiNode(object):
    """
    Class to represent nodes (users) in the network. Name is the username. tweets is the list of tweets (EloiTweet objects) made by the user.
    """
    def __init__(self, name = None, user_id = None, tweets = []):

        if len(tweets) == 0:
            self.name = name
            self.id = user_id
            return

        self.name = tweets[0].user
        self.id = tweets[0].user_id
        self.tweets = tweets
        self.tweets_id = [twe.id for twe in tweets]

        self.descr = tweets[0].user_descr
        self.followers = tweets[0].user_followers
        self.following = tweets[0].user_following
        self.geo_enabled = tweets[0].user_geo_enabled
        self.user_location = tweets[0].user_location
        self.lang = tweets[0].lang

        loc_types = [twe.loc_type for twe in tweets]
        if 'Tweet_GEO_ref' in loc_types:
            ind = loc_types.index('Tweet_GEO_ref')
            self.best_coordinates = tweets[ind].loc_coordinates
            self.best_loc_type = 'Tweet_GEO_ref'
        elif 'Tweet_GEO_tag' in loc_types:
            ind = loc_types.index('Tweet_GEO_tag')
            self.best_coordinates = tweets[ind].loc_coordinates
            self.best_loc_type = 'Tweet_GEO_tag'
        else:
            try:
                self.best_coordinates = find_coords_of_place(self.user_location)
                self.best_loc_type = 'User_location'
            except:
                self.best_coordinates = (np.nan,np.nan)
                self.best_loc_type = None

        self.tweet_count = tweets[0].user_tw_count
        self.timezone = tweets[0].user_timezone

        self.points_to = []
        for twe in tweets:
            self.points_to += twe.link_to
        self.pointed_by = []
        self.num_tweets = len(tweets)
        self.active_interactions = len(self.points_to)
        self.passive_interactions = len(self.pointed_by)
        self.mentions = len([lin for lin in self.pointed_by if lin.type == 'Mention'])
        self.retweeted = len([lin for lin in self.pointed_by if lin.type == 'Retweet'])

        return

    # def extract_from_tweet(self, tweet):
    #     self.name = tweet.user
    #     self.id = tweet.user_id
    #     self.tweets_id.append(tweet.tweet_id)
    #     self.num_tweets += 1
    #     self.points_to = self.points_to + tweet.link_to
    #     self.active_interactions = len(self.points_to)
    #     return

    def add_tweet_to_user(self, tweet):
        #Check if it's already there
        if tweet.id in self.tweets_id:
            print('Tweet already considered, skipping..\n')
            return
        self.tweets_id.append(tweet.id)
        self.points_to = self.points_to + tweet.link_to
        self.num_tweets += 1
        self.active_interactions = len(self.points_to)
        return

    def complete_interactions(self, link_list):
        """
        link_list is a list of EloiLink objects in which Node is the node_B of the connection, the receiver of the interaction. Tipically link_list comes from the EloiNetwork object.
        """
        self.passive_interactions = len(link_list)
        self.pointed_by = link_list
        self.mentions = len([lin for lin in self.pointed_by if lin.type == 'Mention'])
        self.retweeted = len([lin for lin in self.pointed_by if lin.type == 'Retweet'])

        return

    def sum_links(self):
        """
        Adds two attributes that represent the incoming and outgoing relations, summing on all single links. (EloiLinkSum objects)
        """

        point_to = [link for link in self.points_to]
        point_to_user = [link.id_B for link in self.points_to]
        try:
            pointed_by = [link for link in self.pointed_by]
            pointed_by_user = [link.id_A for link in self.pointed_by]
        except Exception as cazzillo:
            print(cazzillo)
            PrintEmph('Have you run the EloiNode.complete_interactions() method first??')
            raise cazzillo

        self.sum_point_to = []
        for user in point_to_user:
            links_to_user = [link for link in point_to if link.id_B == user]
            link_sums = EloiLinkSum(links_to_user, self.id)
            self.sum_point_to.append(link_sums)

        self.sum_pointed_by = []
        for user in pointed_by_user:
            links_to_user = [link for link in pointed_by if link.id_A == user]
            link_sums = EloiLinkSum(links_to_user, user)
            self.sum_pointed_by.append(link_sums)

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


def read_json(filename, tweet_format = 'eloi'):
    """
    Reads json formatted file. Returns list of tweets in format of python dicts.
    :param tweet_format: if 'twitter' the output is a list of twitter.api.TwitterDictResponse, if 'eloi' the class EloiTweet is used.
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
            #raise
            # read in a line is not in JSON format (sometimes errors occur)
            continue

    return Tweets


def load_stream(folder, tag = None, tweet_format = 'eloi'):
    """
    Loads the tweets contained in folder. If tag is specified, only filenames containing tag are considered. Returns list of Tweet objects.
    """
    lista_filez = os.listdir(folder)

    tweets = []

    if tag is not None:
        lista = [fil for fil in lista_filez if tag in fil]
    else:
        lista = lista_filez

    for fil in lista:
        tweets_fil = read_json(folder+fil, tweet_format = tweet_format)
        tweets += tweets_fil

    return tweets


def export_csv(filename, key_names, node_list, delimiter = '\t'):
    """
    Export csv file to be imported in gephi.
    """

    import csv
    #tbf.export_csv(links_A, links_B)
    filos = open(filename, 'w')
    filecsv = csv.writer(filos,delimiter='\t')
    # Writing the keys
    filecsv.writerow(key_names)

    for node in node_list:
        filecsv.writerow(node)

    filos.close()
    return


def export_nodedge_csv(network, cart = None, filelabel = None, export_edges = True, export_nodes = True, export_tweets = True, sum_links = True):
    """
    Exports node csv for all tweets downloaded in folder cart.
    :param network: EloiNetwork object
    :param cart: folder_path
    :param filelabel:
    """
    if cart is None:
        cart = './'

    if filelabel is None:
        filelabel =  network.name

    if export_edges and sum_links:
        cose = network.edges
        coze = []
        for cos,num in zip(cose,range(len(cose))):
            coze.append([cos.id_A,cos.id_B,'Directed',num,cos.name_A+' -> '+cos.name_B,cos.timeset,cos.weight])
        nomi = "source target type id label timeset weight"
        nomis = nomi.split()
        encode_utf8(coze)
        export_csv(cart+filelabel+'_edges.csv', nomis, coze)
    elif export_edges and not sum_links:
        cose = network.all_links
        coze = []
        for cos,num in zip(cose,range(len(cose))):
            coze.append([cos.id_A,cos.id_B,'Directed',num,cos.name_A+' -> '+cos.name_B,cos.created_at,1.0])
        nomi = "source target type id label timestamp weight"
        nomis = nomi.split()
        encode_utf8(coze)
        export_csv(cart+filelabel+'_edges.csv', nomis, coze)

    if export_nodes:
        nomi = "id label timestamp lat lng lang friends_count followers_count"
        cose = network.nodes
        coze = []
        for cos,num in zip(cose,range(len(cose))):
            tweet_id = [twe.id for twe in cos.tweets]
            id_min = np.argmin(np.array(tweet_id))
            timestamp = [twe for twe in cos.tweets][id_min].created_at
            coze.append([cos.id,cos.name,timestamp,cos.best_coordinates[0],cos.best_coordinates[1],cos.lang,cos.following,cos.followers])
        encode_utf8(coze)
        nomis = nomi.split()
        export_csv(cart+filelabel+'_nodes.csv', nomis, coze)

    if export_tweets:
        nomi = "id label user timestamp lat lng lang"
        cose = network.tweets
        coze = []
        for cos,num in zip(cose,range(len(cose))):
            coze.append([cos.id,cos.text,cos.user_id,cos.user_name,cos.created_at,cos.loc_coordinates[0],cos.loc_coordinates[1],cos.lang])
        nomis = nomi.split()
        encode_utf8(coze)
        export_csv(cart+filelabel+'_tweets.csv', nomis, coze)

    return


def encode_utf8(lista):
    """
    Encodes in utf-8 all string elements of list.
    """
    lista_ok = []
    for cos in lista:
        if type(cos) == str:
            cos.encode('utf-8')
        lista_ok.append(cos)

    lista = lista_ok

    return


def encode_ascii(lista):
    """
    Encodes in ascii all string elements of list. ignores non ascii characters.
    """

    lista_ok = []
    for cos in lista:
        if type(cos) == str:
            cos.encode('ascii','ignore')
        lista_ok.append(cos)

    lista = lista_ok

    return
