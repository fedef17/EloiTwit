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
max_try = 10

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

keys = 'access_file folder_path search_string search_label first_file max_id'
keys = keys.split()
itype = [str, str, str, str, int, long]
defaults = [None, '.', None, None, 0, None]
inputs = tbf.read_inputs(input_file, keys, itype = itype, defaults = defaults)

# Run search
for ilk in range(max_try):
    print('Try number {} at {}'.format(ilk,time.ctime()))
    _cart_, first_file_new, max_id_new, status = etl.search(inputs)
    if status:
        break
    else:
        print('----------------------')
        print('----------------------')
        print('Error found. Restarting from where I left.... : max_id = {}, first_file = {}'.format(max_id_new-1,first_file_new+1))
        inputs['max_id'] = max_id_new - 1
        inputs['first_file'] = first_file_new + 1
        continue

print('Results saved in: {}. Stopping program.. ciao!'.format(_cart_))

ok, cazzillo = etl.export_csv_search(_cart_)
if not ok:
    print('Problem in exporting csv..\n')
    raise cazzillo
