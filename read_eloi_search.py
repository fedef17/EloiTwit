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

cart = '/home/fede/Scrivania/Coc/eloi_twit/'

filename = cart + 'output_#WomensMarch_2.dat'
lista = tbf.read_json(filename, tweet_format = 'my_tweet')

print(type(lista),len(lista))

for tw in lista:
    print(type(tw),tw['user']['screen_name'])
    #tw.print_tw()
