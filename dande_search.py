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
import time

import twit_base_funct as tbf
import twitter as tw
import json

# Uses the SEARCH api

quartodora = 15*60

i_0 = 216
user = 2

cart = '/home/fedefab/Scrivania/Idee/eloi_twit/'
search_string = '#WomensMarch'
lab = '{:03d}'
file_out = open(cart + 'dandesearch_'+search_string+lab.format(i_0)+'.dat','w')

#id0 = 822924338672336897 
#id0 = 822915963238678532 # parte da questo!
#id0 = 822837986580721666
id0 = 822821324162732033

oauth = tbf.access(user=user)
if user == 1:
    print('USER is {}\n'.format('titicacaf'))
elif user == 2:
    print('USER is {}\n'.format('d4ndel1on'))
else:
    raise NameError('No user defined!')

# Initiate the connection to Twitter REST API
twitter = tw.Twitter(auth=oauth)

# Search for latest tweets about search_string
# ricerca = twitter.search.tweets(q=search_string, count = 100)

if id0 is not None:
    print(id0,id0-1)
    ricerca = twitter.search.tweets(q=search_string, count = 100, max_id = id0-1, result_type = 'recent')
else:
    ricerca = twitter.search.tweets(q=search_string, count = 100, result_type = 'recent')

t1 = time.time()
print(time.ctime())

search_stat = ricerca['search_metadata']
tweets = ricerca['statuses']

tweet_count = 0
for tweet in tweets:
    if 'text' in tweet:
        json.dump(tweet, file_out)#, indent=4)
        file_out.write('\n')

        tweet_id = tweet['id_str']
        tw_username = tweet['user']['screen_name']
        tw_user_id = tweet['user']['id_str']
        tw_time = tweet['created_at']
        tw_text = tweet['text']

        print('{}: {} at {} --> {}\n'.format(tweet_count, r'@'+tw_username, tw_time, tw_text.encode('utf-8')))
        tweet_count += 1

#max_id = search_stat['max_id'] # A me in realtà servirebbe il min id

for times in range(i_0,i_0+200):
    print('times',times)
    if times > i_0:
        file_out = open(cart + 'dandesearch_'+search_string+lab.format(times)+'.dat','w')
        t1 = time.time()
        print(time.ctime())
    for tri in range(170):
        if tri%10 == 0:
            print(tri)
            done = False
            trials = 0
            while not done:
                trials+=1
                try:
                    quantoresta = twitter.application.rate_limit_status(resources='search')
                    restano = quantoresta['resources']['search']['/search/tweets']['remaining']
                    print('Restano {} richieste\n'.format(restano))
                    done = True
                except:
                    time.sleep(30)
                if trials > 10:
                    restano = 0
                    break
            if restano < 10:
                print('PROBLEMA! esco\n')
                break
        max_id = np.max(np.array([t['id'] for t in tweets]))
        time_max_id = np.argmax(np.array([t['id'] for t in tweets]))
        max_time = tweets[time_max_id]['created_at']
        print('max_id: {}; time: {}'.format(max_id,max_time))
        min_id = np.min(np.array([t['id'] for t in tweets]))
        time_min_id = np.argmin(np.array([t['id'] for t in tweets]))
        min_time = tweets[time_min_id]['created_at']
        print('min_id: {}; time: {}'.format(min_id,min_time))
        print('\n')

        try:
	    ricerca = twitter.search.tweets(q=search_string, count = 100, max_id = min_id-1, result_type = 'recent')

            search_stat = ricerca['search_metadata']
            tweets = ricerca['statuses']

            for tweet in tweets:
                if 'text' in tweet:
                    json.dump(tweet, file_out)#, indent=4)
                    file_out.write('\n')
                    tweet_count += 1
        except:
	    continue

    print('Siamo a {} tweets\n'.format(tweet_count))

    print('--------------------------------------------------\n')
    try:
        quantoresta = twitter.application.rate_limit_status(resources='search')
        restano = quantoresta['resources']['search']['/search/tweets']['remaining']
        print('Restano {} richieste\n'.format(restano))
    except:
        print('Error in retrieving remaining requests')
        restano = -1
    print('--------------------------------------------------\n')

    t2 = time.time()
    tdiff = t2-t1
    if tdiff < quartodora:
        manca = quartodora - tdiff
    else:
 	manca = 4
    print(time.ctime())
    print('Ora aspetto {} secondi.\n'.format(manca+20))
    time.sleep(manca+20)
    print(time.ctime())

    print('--------------------------------------------------\n')
    try:
        quantoresta = twitter.application.rate_limit_status(resources='search')
        restano = quantoresta['resources']['search']['/search/tweets']['remaining']
        print('Restano {} richieste\n'.format(restano))
    except:
        print('Error in retrieving remaining requests')
        restano = -1
    while restano != 180:
        print('PROBLEMA!\n')
        time.sleep(60)
        try:
            quantoresta = twitter.application.rate_limit_status(resources='search')
            restano = quantoresta['resources']['search']['/search/tweets']['remaining']
            print('Restano {} richieste\n'.format(restano))
        except:
            print('Error in retrieving remaining requests')
            restano = -1
    print('--------------------------------------------------\n')
    file_out.close()
