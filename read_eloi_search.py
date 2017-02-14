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
cart = '/media/fede/fedata/eloi_twit/'

lista_tweets = open(cart + 'lista_tweets.dat','r')

tweets = []
ii = 0
for filename in lista_tweets.readlines():
    print(filename.rstrip())
    lista = tbf.read_json(cart + filename.rstrip(), tweet_format = 'eloi')
    tweets += lista
    ii += 1
    if ii == 10: break


#print(lista[0].favorite_count, lista[0].link_to[0].start, lista[0].link_to[0].end, lista[0].link_to[0].type)
# print(type(lista[0]))
# sys.exit()
# print(type(lista),len(lista))
#
# for tw in lista:
#     print(type(tw),tw.user_name, tw.media_type, tw.url_links)#['user']['screen_name'])
#     #tw.print_tw()
