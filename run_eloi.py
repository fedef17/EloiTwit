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
import eloi_tools_library as etl
from multiprocessing import Pool


# Read options/arguments given to the code
args = tbf.parseArguments('search')

# Redirects standard output
if not args.live:
    sys.stdout = open(args.log, 'w')

time_init = time.time()

# Reads input file
try:
    todo_file = args.todo_file
    if not os.path.isfile(todo_file):
        raise ValueError('No todo_file given, setting the default ./eloi_todo.in')
except:
    print('No todo_file specified, setting the default ./eloi_todo.in')
    todo_file = './eloi_todo.in'
    if not os.path.isfile(todo_file):
        raise ValueError('No todo_file found, give the file path as argument to the code (python eloi_search.py /path/to/eloi_todo.in) or place it in this folder')

#### READS INPUTS from todo_file ################

#todo_file = open(todo_file,'r')

keys = 'ht_list_file input_file_search settings_file'
keys = keys.split()
itype = [str, str, str]
defaults = ['./ht_list.in','./eloi_input.in','./eloi_settings.set']
input_files = tbf.read_inputs(todo_file, keys, itype = itype, defaults = defaults)

# NOW READING THE HASHTAG LIST FROM ht_list.
with open(input_files['ht_list_file'],'r') as filist:
    ht_list = json.load(filist)['wordTracking']

# DEVO LEGGERE ANCHE ELOI_INPUT E I SETTINGS......

access_files = ['/home/fedefab/Scrivania/Idee/eloi_twit/access_tokens/user_2.acc', '/home/fedefab/Scrivania/Idee/eloi_twit/access_tokens/user_1.acc']
access_available = np.array([True, True])

# while np.any(access_available):

carts = []

# pool = Pool(processes=2)
#     parsed = pool.apply_async()
#     pattern = pool.apply_async(Process2, [bigfile])
#     calc_res = pool.apply_async(Process3, [integer])
#
#     pool.close()
#     pool.join()
#
#     final = FinalProcess(parsed.get(), pattern.get(), calc_res.get())

for ht in ht_list:
    try:
        search_string = '#'+str(ht.strip())
    except Exception as cazzillo:
        print(cazzillo)
        continue

    # Run search
        #### READS INPUTS from input_file ################
    keys = 'access_file folder_path search_string search_label first_file max_id'
    keys = keys.split()
    itype = [str, str, str, str, int, long]
    defaults = [None, None, None, None, 0, None]

    accfile = access_files[0]

    inputs = dict(zip(keys,defaults))
    inputs['access_file'] = accfile
    inputs['search_string'] = search_string

    _cart_ = etl.search(inputs)
    carts.append(_cart_)

    #tbf.export_nodedge_csv(_cart_)
