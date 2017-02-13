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

cart = '/home/fede/Scrivania/Idee/eloi_twit/'

#filename = '/media/fede/fedata/eloi_twit/dandesearch_#WomensMarch000.dat'
filename = cart + 'dandesearch_#WomensMarch000.dat'
lista = tbf.read_json(filename, tweet_format = 'eloi')
#print(lista[0].favorite_count, lista[0].link_to[0].start, lista[0].link_to[0].end, lista[0].link_to[0].type)
# print(type(lista[0]))
# sys.exit()
print(type(lista),len(lista))

for tw in lista[0:2]:
    print(type(tw),tw.user_name, tw.text)#['user']['screen_name'])
    #tw.print_tw()
