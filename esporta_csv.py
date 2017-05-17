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

cart0 = '/media/hd_B/DATA/Twitter_eloi/'
filecarts = '/home/fedefab/Scrivania/Idee/eloi_twit/eloipy/export_carts.in'
fileo = open(filecarts,'r')

for cart in fileo.readlines():
    ok, cazzillo = etl.export_csv_search(cart0+cart.rstrip())
    if ok: print('Tutto ok per cart: {}'.format(cart))

fileo.close()
