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

#cart = '/home/fedefab/Scrivania/Idee/eloi_twit/'
cart = '/home/fedefab/Scrivania/Idee/eloi_twit/LottoMarzo_search/'
cart = '/home/fedefab/Scrivania/Idee/eloi_twit/SanValentino2017_search/'

# geolocation_file = '/home/fedefab/Scrivania/Idee/eloi_twit/eloipy/worldcitiespop.txt'
#
# # Loads the names and coordinates contained in geolocation_file
# countries = ['us','it','gb','es','fr','de']
# all_places = []
# with open(geolocation_file) as infile:
#     infile.readline()
#     for line in infile.readlines():
#         linea = line.split(',')
#         if linea[0] in countries:
#             print(linea[0])
#             linea_ok = [linea[0],linea[1],linea[3],float(linea[5]),float(linea[6])]
#             all_places.append(linea_ok)
#
# print(len(all_places))


# Reads all the tweets in folder
tweets = tbf.load_stream(cart, tag = None)

nodes = np.unique(np.array([twe.user_name for twe in tweets]))
links_A = [lin.name_A for lin in twe.link_to]

links_A = []
links_B = []
for twe in tweets:
    links_A += [lin.name_A for lin in twe.link_to]
    links_B += [lin.name_B for lin in twe.link_to]

#tbf.export_csv(links_A, links_B)
file = open(cart + 'links.csv', 'w')
import csv
filecsv = csv.writer(file,delimiter='\t')

for A, B in zip(links_A, links_B):
    filecsv.writerow([A,B])


    # data = np.array([line.split(',') for line in infile.readlines() if line.split(',')[0] in countries])
    # data = np.array([data[:,0],data[:,1],data[:,3],map(float,data[:,5]),map(float,data[:,6])])

#
#
# lista_tweets = open(cart + 'lista_tweets.dat','r')
#
# tweets = []
# ii = 0
# for filename in lista_tweets.readlines():
#     print(filename.rstrip())
#     lista = tbf.read_json(cart + filename.rstrip(), tweet_format = 'eloi')
#     tweets += lista
#     ii += 1
#     if ii == 10: break
#
#
# #print(lista[0].favorite_count, lista[0].link_to[0].start, lista[0].link_to[0].end, lista[0].link_to[0].type)
# # print(type(lista[0]))
# # sys.exit()
# # print(type(lista),len(lista))
# #
# # for tw in lista:
# #     print(type(tw),tw.user_name, tw.media_type, tw.url_links)#['user']['screen_name'])
# #     #tw.print_tw()
