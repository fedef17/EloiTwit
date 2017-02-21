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
args = tbf.parseArguments('stream')

# Redirects standard output
if not args.live:
    sys.stdout = open(args.log, 'w')

verbose = args.verbose

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

keys = 'access_file folder_path search_string search_label max_files first_file tweets_per_file'
keys = keys.split()
itype = [str, str, str, str, int, int, int]
defaults = [None, '.', None, None, 10000, 0, 1000]
inputs = tbf.read_inputs(input_file, keys, itype = itype, defaults = defaults)

if inputs['folder_path'] == '.':
    print('Setting the current folder as output folder')
cart = inputs['folder_path']

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
####### --------------------------------------- #####
###### IMPORTANT:: ::: STREAMING seems not to work with the urrlib.quote, not like the search API.... But works without! :D
#search_string = urllib.quote(inputs['search_string'])
####### --------------------------------------- #####
search_string = inputs['search_string']
print('SEARCHING FOR: {}\n'.format(inputs['search_string']))

if inputs['search_label'] is None:
    search_label = inputs['search_string'][0:25]
    print('Setting auto search_label: {}'.format(search_label))

i_0 = inputs['first_file']

if inputs['max_files'] < 1000:
    lab = '{:03d}'
elif inputs['max_files'] < 100000:
    lab = '{:05d}'
else:
    lab = '{:06d}'

tweets_per_file = inputs['tweets_per_file']

tbf.PrintEmph('Streaming begins.')

# Checks internet connection
if not tbf.internet_on():
    NoConnection = not tbf.wait_connection()

# Initiate the connection to Twitter Streaming API
oauth = tbf.access_from_file(inputs['access_file'])
twitter_stream = tw.TwitterStream(auth=oauth)

# Get a sample of the public data following through Twitter
iterator = twitter_stream.statuses.filter(track = search_string)

n_file = i_0
tweet_count = 0
missing_tweets = 0
NoMoreTweets = False
EndOfResearch = False

# Opens the first file
outfile = cart+search_label+'_'+lab.format(n_file)+'.dat'
file_out = open(outfile, 'w')
print('File: {}\n'.format(outfile))

for tweet in iterator:
    ### Write tweets to file_out
    try:
        if 'text' in tweet:
            json.dump(tweet, file_out)
            file_out.write('\n')
            tweet_count += 1
            last_id = tweet['id']
            missing_tweets = 0
            if verbose: print('Downloaded tweet {}, created at {}'.format(tweet['id'],tweet['created_at']))
    except Exception as cazzillo:
        print('Found exception: {}'.format(cazzillo))
        missing_tweets +=1
        print('LAST ID DOWNLOADED: {}'.format(last_id))
        Connected = tbf.wait_connection()
        if Connected and missing_tweets % 5 == 0:
            tbf.PrintEmph('PROBLEM: More than {} tweets missed.. This is weird -> Try to STOP and reRUN the code!'.format(missing_tweets))
            if missing_tweets > 100:
                NoMoreTweets = True

    # Closes the file if already tweets_per_file tweets have been collected
    if tweet_count % tweets_per_file == 0:
        file_out.close()
        n_file += 1
        outfile = cart+search_label+'_'+lab.format(n_file)+'.dat'
        file_out = open(outfile, 'w')
        print('File: {}\n'.format(outfile))

    if tweet_count == inputs['max_files']*tweets_per_file:
        file_out.close()
        break

    if NoMoreTweets:
        file_out.close()
        EndOfResearch = True
        break

time_tot = time.time() - time_init

tbf.PrintEmph('STREAMING endend with {} tweets, downloaded in {:4.1f} hours'.format(tweet_count, time_tot/3600.))

if EndOfResearch:
    tbf.PrintEmph('<<- EloiTwit ->> STREAMING ENDED -- No More Tweets available with your search_string. Bye!\n', level=2)
