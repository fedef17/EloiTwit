#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import sys
import os.path
import matplotlib.pyplot as pl
import math as mt
import matplotlib.colors as colors
import scipy.stats as stats
import time
from subprocess import call

import twit_base_funct as tbf
import twitter as tw
import json
import urllib
import urllib2
import argparse


# Read options/arguments given to the code
args = tbf.parseArguments('search')

# Redirects standard output
if not args.live:
    sys.stdout = open(args.log, 'w')

time_init = time.time()

# Reads input file
try:
    input_file = args.input_file
    if not os.path.isfile(input_file):
        raise ValueError('No input_file given, setting the default ./eloi_input.in')
except:
    print('No input_file specified, setting the default ./eloi_input.in')
    input_file = './eloi_input.in'
    if not os.path.isfile(input_file):
        raise ValueError('No input_file found, give the file path as argument to the code (python eloi_search.py /path/to/eloi_input.in) or place it in this folder')

#### READS INPUTS from input_file ################

keys = 'access_file folder_path search_string search_label max_files first_file max_id'
keys = keys.split()
itype = [str, str, str, str, int, int, long]
defaults = [None, '.', None, None, 1000, 0, None]
inputs = tbf.read_inputs(input_file, keys, itype = itype, defaults = defaults)

if inputs['folder_path'] == '.':
    print('Setting the current folder as output folder')
cart = inputs['folder_path']

if not os.path.exists(cart):
    os.mkdir(cart)

if inputs['access_file'] is None:
    access_file = cart+'access_file.acc'
else:
    access_file = inputs['access_file']
if not os.path.isfile(access_file):
    raise ValueError('access_file not found at {}!'.format(access_file))

if inputs['search_string'] is None:
    raise ValueError('What should I search for? Set [search_string].\n')

oauth = tbf.access_from_file(inputs['access_file'])

tbf.PrintEmptyLine()
search_string = urllib.quote(inputs['search_string'])
print('SEARCHING FOR: {}\n'.format(inputs['search_string']))

if inputs['search_label'] is None:
    search_label = inputs['search_string'][0:25]
    print('Setting auto search_label: {}'.format(search_label))

max_id = inputs['max_id']
i_0 = inputs['first_file']

if max_id is None:
    print('Research starts from most recent tweet\n')

tbf.PrintEmph('Cycle begins.')

if inputs['max_files'] < 1000:
    lab = '{:03d}'
elif inputs['max_files'] < 100000:
    lab = '{:05d}'
else:
    lab = '{:06d}'

time_sleep = 4
quartodora = 15*60.
tweet_count = 0

NoMoreTweets = False # Checks when no more tweets are avilable
EndOfResearch = False # True only if research ended and no fatal errors occurred

###### Beginning the cycle on 15 min sessions ##############

for times in range(i_0,i_0+inputs['max_files']):
    missing_tweets = 0

    # Checks internet connection
    if not tbf.internet_on():
        NoConnection = not tbf.wait_connection()

    # Initiate the connection to Twitter REST API
    try:
        oauth = tbf.access_from_file(inputs['access_file'])
        twitter = tw.Twitter(auth=oauth)
    except Exception as cazzillo:
        print('Trying again, {}'.format(cazzillo))
        oauth = tbf.access_from_file(inputs['access_file'])
        twitter = tw.Twitter(auth=oauth)

    outfile = cart+search_label+'_'+lab.format(times)+'.dat'
    file_out = open(outfile, 'w')
    print('File: {}\n'.format(outfile))

    # Waits for the 180 requests to be available
    ok_180, restano = tbf.wait_requests(twitter, sleep_time = time_sleep, wait = True, interval = 60, n_trials = 15, num_min = 100)

    if not ok_180:
        if restano is not None:
            print('PROBLEM! Only {} requests left for cycle {}. Closing cycle and waiting..\n'.format(restano,times))
        if NoConnection:
            print('PROBLEM! No Internet connection, closing cycle {} and waiting...\n'.format(times))
        file_out.close()
        continue

    # comincio a contare il tempo
    t1 = time.time()
    print(time.ctime())

    #### Beginning cycle over the 180 requests (170 here, just to be sure) #####
    for tri in range(170):
        if tri%10 == 0:
            print('Made {} out of {} requests for cycle {}\n'.format(tri, 170, times))

            # Checking remaining requests
            try:
                ok_bool, restano = tbf.wait_requests(twitter, num_min = 11)
            except Exception as cazzillo:
                print('Trying again, {}'.format(cazzillo))
                ok_bool, restano = tbf.wait_requests(twitter, num_min = 11)

            if restano is not None and restano < 11:
                print('PROBLEM! Only {} requests missing, closing cycle {}\n'.format(restano, times))
                file_out.close()
                break
            elif not ok_bool:
                print('PROBLEM! Closing cycle {} and waiting...\n'.format(times))
                file_out.close()
                break

        # Making the request:
        try:
            ricerca = twitter.search.tweets(q=search_string, count = 100, max_id = max_id, result_type = 'recent')

            search_stat = ricerca['search_metadata']
            tweets = ricerca['statuses']

            if len(tweets) == 0:
                missing_tweets += 1
                if missing_tweets > 5:
                    NoMoreTweets = True
                    break
                continue

            ### Write tweets to file_out
            for tweet in tweets:
                if 'text' in tweet:
                    json.dump(tweet, file_out)
                    file_out.write('\n')
                    tweet_count += 1

            # Max and Min ids of this search
            max_id = np.max(np.array([t['id'] for t in tweets]))
            time_max_id = np.argmax(np.array([t['id'] for t in tweets]))
            max_time = tweets[time_max_id]['created_at']
            print('max_id: {}; time: {}'.format(max_id,max_time))

            min_id = np.min(np.array([t['id'] for t in tweets]))
            time_min_id = np.argmin(np.array([t['id'] for t in tweets]))
            min_time = tweets[time_min_id]['created_at']
            print('min_id: {}; time: {}'.format(min_id,min_time))
            print('\n')

            # Finding the max id for the next iteration
            max_id = min_id - 1
        except Exception as cazzillo:
            print('------>> Found exception {} <<-------'.format(type(cazzillo)))
            raise
            continue

    print('Siamo a {} tweets\n'.format(tweet_count))
    tbf.PrintBreakLine()


# Read options/arguments given to the code
args = tbf.parseArguments('search')

# Redirects standard output
if not args.live:
    sys.stdout = open(args.log, 'w')

time_init = time.time()

# Reads input file
try:
    input_file = args.input_file
    if not os.path.isfile(input_file):
        raise ValueError('No input_file given, setting the default ./eloi_input.in')
except:
    print('No input_file specified, setting the default ./eloi_input.in')
    input_file = './eloi_input.in'
    if not os.path.isfile(input_file):
        raise ValueError('No input_file found, give the file path as argument to the code (python eloi_search.py /path/to/eloi_input.in) or place it in this folder')

#### READS INPUTS from input_file ################

keys = 'access_file folder_path search_string search_label max_files first_file max_id'
keys = keys.split()
itype = [str, str, str, str, int, int, long]
defaults = [None, '.', None, None, 1000, 0, None]
inputs = tbf.read_inputs(input_file, keys, itype = itype, defaults = defaults)

if inputs['folder_path'] == '.':
    print('Setting the current folder as output folder')
cart = inputs['folder_path']

if not os.path.exists(cart):
    os.mkdir(cart)

if inputs['access_file'] is None:
    access_file = cart+'access_file.acc'
else:
    access_file = inputs['access_file']
if not os.path.isfile(access_file):
    raise ValueError('access_file not found at {}!'.format(access_file))

if inputs['search_string'] is None:
    raise ValueError('What should I search for? Set [search_string].\n')

oauth = tbf.access_from_file(inputs['access_file'])

tbf.PrintEmptyLine()
search_string = urllib.quote(inputs['search_string'])
print('SEARCHING FOR: {}\n'.format(inputs['search_string']))

if inputs['search_label'] is None:
    search_label = inputs['search_string'][0:25]
    print('Setting auto search_label: {}'.format(search_label))

max_id = inputs['max_id']
i_0 = inputs['first_file']

if max_id is None:
    print('Research starts from most recent tweet\n')

tbf.PrintEmph('Cycle begins.')

if inputs['max_files'] < 1000:
    lab = '{:03d}'
elif inputs['max_files'] < 100000:
    lab = '{:05d}'
else:
    lab = '{:06d}'

time_sleep = 4
quartodora = 15*60.
tweet_count = 0

NoMoreTweets = False # Checks when no more tweets are avilable
EndOfResearch = False # True only if research ended and no fatal errors occurred

###### Beginning the cycle on 15 min sessions ##############

for times in range(i_0,i_0+inputs['max_files']):
    missing_tweets = 0

    # Checks internet connection
    if not tbf.internet_on():
        NoConnection = not tbf.wait_connection()

    # Initiate the connection to Twitter REST API
    try:
        oauth = tbf.access_from_file(inputs['access_file'])
        twitter = tw.Twitter(auth=oauth)
    except Exception as cazzillo:
        print('Trying again, {}'.format(cazzillo))
        oauth = tbf.access_from_file(inputs['access_file'])
        twitter = tw.Twitter(auth=oauth)

    outfile = cart+search_label+'_'+lab.format(times)+'.dat'
    file_out = open(outfile, 'w')
    print('File: {}\n'.format(outfile))

    # Waits for the 180 requests to be available
    ok_180, restano = tbf.wait_requests(twitter, sleep_time = time_sleep, wait = True, interval = 60, n_trials = 15, num_min = 100)

    if not ok_180:
        if restano is not None:
            print('PROBLEM! Only {} requests left for cycle {}. Closing cycle and waiting..\n'.format(restano,times))
        if NoConnection:
            print('PROBLEM! No Internet connection, closing cycle {} and waiting...\n'.format(times))
        file_out.close()
        continue

    # comincio a contare il tempo
    t1 = time.time()
    print(time.ctime())

    #### Beginning cycle over the 180 requests (170 here, just to be sure) #####
    for tri in range(170):
        if tri%10 == 0:
            print('Made {} out of {} requests for cycle {}\n'.format(tri, 170, times))

            # Checking remaining requests
            try:
                ok_bool, restano = tbf.wait_requests(twitter, num_min = 11)
            except Exception as cazzillo:
                print('Trying again, {}'.format(cazzillo))
                ok_bool, restano = tbf.wait_requests(twitter, num_min = 11)

            if restano is not None and restano < 11:
                print('PROBLEM! Only {} requests missing, closing cycle {}\n'.format(restano, times))
                file_out.close()
                break
            elif not ok_bool:
                print('PROBLEM! Closing cycle {} and waiting...\n'.format(times))
                file_out.close()
                break

        # Making the request:
        try:
            ricerca = twitter.search.tweets(q=search_string, count = 100, max_id = max_id, result_type = 'recent')

            search_stat = ricerca['search_metadata']
            tweets = ricerca['statuses']

            if len(tweets) == 0:
                missing_tweets += 1
                if missing_tweets > 5:
                    NoMoreTweets = True
                    break
                continue

            ### Write tweets to file_out
            for tweet in tweets:
                if 'text' in tweet:
                    json.dump(tweet, file_out)
                    file_out.write('\n')
                    tweet_count += 1

            # Max and Min ids of this search
            max_id = np.max(np.array([t['id'] for t in tweets]))
            time_max_id = np.argmax(np.array([t['id'] for t in tweets]))
            max_time = tweets[time_max_id]['created_at']
            print('max_id: {}; time: {}'.format(max_id,max_time))

            min_id = np.min(np.array([t['id'] for t in tweets]))
            time_min_id = np.argmin(np.array([t['id'] for t in tweets]))
            min_time = tweets[time_min_id]['created_at']
            print('min_id: {}; time: {}'.format(min_id,min_time))
            print('\n')

            # Finding the max id for the next iteration
            max_id = min_id - 1
        except Exception as cazzillo:
            print('------>> Found exception {} <<-------'.format(type(cazzillo)))
            raise
            continue

    print('Siamo a {} tweets\n'.format(tweet_count))
    tbf.PrintBreakLine()

    try:
        quantoresta = twitter.application.rate_limit_status(resources='search')
        restano = quantoresta['resources']['search']['/search/tweets']['remaining']
        print('Restano {} richieste\n'.format(restano))
    except Exception as cazzillo:
        print('------>> Found exception {} <<-------'.format(type(cazzillo)))
        print('Error in retrieving remaining requests')
        restano = -1
    tbf.PrintBreakLine()

    # Estimate how much time we should wait
    t2 = time.time()
    tdiff = t2-t1
    if tdiff < quartodora:
        time_sleep = quartodora - tdiff
    else:
        time_sleep = 4
    print(time.ctime())

    # Closing file and starting new cycle
    file_out.close()

    # Closing research if no more tweets are available
    if NoMoreTweets:
        EndOfResearch = True
        break

time_tot = time.time() - time_init

tbf.PrintEmph('SEARCH endend with {} tweets, downloaded in {:4.1f} hours'.format(tweet_count, time_tot/3600.))

if EndOfResearch:
    tbf.PrintEmph('<<- EloiTwit ->> RESEARCH ENDED -- No More Tweets available with your search_string. Bye!\n', level=2)

    try:
        quantoresta = twitter.application.rate_limit_status(resources='search')
        restano = quantoresta['resources']['search']['/search/tweets']['remaining']
        print('Restano {} richieste\n'.format(restano))
    except Exception as cazzillo:
        print('------>> Found exception {} <<-------'.format(type(cazzillo)))
        print('Error in retrieving remaining requests')
        restano = -1
    tbf.PrintBreakLine()

    # Estimate how much time we should wait
    t2 = time.time()
    tdiff = t2-t1
    if tdiff < quartodora:
        time_sleep = quartodora - tdiff
    else:
        time_sleep = 4
    print(time.ctime())

    # Closing file and starting new cycle
    file_out.close()

    # Closing research if no more tweets are available
    if NoMoreTweets:
        EndOfResearch = True
        break

time_tot = time.time() - time_init

tbf.PrintEmph('SEARCH endend with {} tweets, downloaded in {:4.1f} hours'.format(tweet_count, time_tot/3600.))

if EndOfResearch:
    tbf.PrintEmph('<<- EloiTwit ->> RESEARCH ENDED -- No More Tweets available with your search_string. Bye!\n', level=2)


#time_str = time.ctime().split()
#time_stamp = '_'+time_str[2]+'-'+time_str[1]+'-'+time_str[4]
#nome_log_0 = cart+'log_'+search_label+time_stamp
#nome_log = nome_log_0 + '.log'
#iui = 1
#while os.path.isfile(nome_log):
#    nome_log = nome_log_0 + '{:02d}'.format(iui) + '.log'
#    iui += 1
#
#call(["echo pippo"])
#call(["cp log_eloi_search.log "+nome_log])
