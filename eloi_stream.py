#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import sys
import os.path
import matplotlib.pyplot as pl
import math as mt
import spect_base_module as sbm
import pickle
import scipy.io as io
import matplotlib.colors as colors
import scipy.stats as stats

import twit_base_funct as tbf
import twitter as tw
import json

## Uses the STREAMING API

cart = '/home/fede/Scrivania/Coc/eloi_twit/'
search_string = '#WomensMarch'
file_out = open(cart + 'output_'+search_string+'_2.dat','w')

# filename = cart + 'output_#WomensMarch_2.dat'
# lista = tbf.read_json(filename, tweet_format = 'my_tweet')
#
# print(type(lista),len(lista))
#
# for tw in lista:
#     print(type(tw),tw['user']['screen_name'])
#     #tw.print_tw()
#
# sys.exit()

oauth = tbf.access()

# Initiate the connection to Twitter Streaming API
twitter_stream = tw.TwitterStream(auth=oauth)

# Get a sample of the public data following through Twitter
iterator = twitter_stream.statuses.filter(track = search_string)

# Print each tweet in the stream to the screen
# Here we set it to stop after getting 1000 tweets.
# You don't have to set it to stop, but can continue running
# the Twitter API to collect data for days or even longer.

print(type(iterator))
tweet_count = 100
for tweet in iterator: # ognuno di questi è un json. Falso. è un twitter.api.TwitterDictResponse
    tweet_count -= 1

    # Twitter Python Tool wraps the data returned by Twitter
    # as a TwitterDictResponse object.
    # We convert it back to the JSON format to print/score
    if 'text' in tweet:
        #tweet_json = json.dumps(tweet,indent=4)
        json.dump(tweet, file_out)#, indent=4)
        file_out.write('\n')

        tweet_id = tweet['id_str']
        username = tweet['user']['screen_name']
        user_id = tweet['user']['id_str']
        time = tweet['created_at']
        text = tweet['text']

        try:
            reply_to_user = tweet['in_reply_to_screen_name']
            reply_to_tweet_id_str = tweet['in_reply_to_status_id_str']
            flag_reply = True
        except:
            reply_to_user = None
            reply_to_tweet_id_str = None
            flag_reply = False

        try:
            rt = tweet['retweeted_status']
            retweeted_user = rt['user']['screen_name']
            retweeted_tweet_id = rt['id_str']
            flag_retweet = True
        except:
            flag_retweet = False
            retweeted_user = None
            retweeted_tweet_id = None

        try:
            qt = tweet['quoted_status']
            quoted_user = qt['user']['screen_name']
            quoted_tweet_id = tweet['quoted_status_id_str']
            flag_quote = True
        except:
            flag_quote = False
            quoted_tweet_id = None
            quoted_user = None

        #print('{}: {} at {} --> {}\n'.format(tweet_count, tweet['user']['name'], tweet['created_at'],tweet['text']))
        print('{}: {} at {} --> {}\n'.format(tweet_count, r'@'+username, time, text.encode('utf-8')))

    # The command below will do pretty printing for JSON data, try it out
    # print json.dumps(tweet, indent=4)

    if tweet_count <= 0:
        break

file_out.close()
