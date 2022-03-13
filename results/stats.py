#!/usr/bin/env python3

import statistics as stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json

def load_json(file):
    try:
        with open(file, "r") as fp:
            results = json.load(fp)
            return results
    except Exception as e:
        print(e)

def unpack_list(r):
    l=[]
    for t in r:
        for e in r[t]:
            l.append(e)
    l.sort()
    return l

def zscore(x,mean,std):
    z=(x-mean)/std
    return z

def img_show(bel_means,mean,std):
    img=np.zeros((30,22),dtype=float)
    x=0
    y=0
    for b in bel_means:
        #x and y swapped for graph
        img[y,x]=zscore(b,mean,std)
        y+=1
        if 30==y:
            x+=1
            y=0
    graph=plt.imshow(img,interpolation='None',origin='lower')
    graph_colorbar=plt.colorbar(graph)
    graph_colorbar.set_label('Z-Score')
    plt.suptitle('iCEBreaker FPGA BEL Variance',x=.54,fontsize=12)
    plt.title('Ram columns omitted', fontsize=10)
    plt.show()

def histogram(bel_means):
    fig,ax=plt.subplots()
    bel_zscores=bel_means
    ax.hist(bel_zscores,bins=30)
    plt.title('iCEBreaker FPGA BEL Frequency Distribution')
    plt.xlabel('Ring Oscillator Frequency (MHz)')
    plt.show()
    
def result_stats(file_name):
    #load data
    results_panda=pd.read_json(file_name)
    results_list=unpack_list(load_json(file_name))

    #panda values are per bel(by column)
    panda_min=results_panda.min()
    panda_max=results_panda.max()
    panda_mean=results_panda.mean()
    panda_stdev=results_panda.std()
    panda_median=results_panda.median()
    panda_variance=results_panda.var()

    #list values are overall(all bels combined)
    list_min=results_list[0]
    list_max=results_list[len(results_list)-1]
    list_mean=stats.mean(results_list)
    list_std=stats.stdev(results_list,list_mean)
    list_variance=stats.variance(results_list,list_mean)

    #graphs
    img_show(panda_mean,list_mean,list_std)
    histogram(panda_mean)

    #info
    print(file_name)
    print('Min:',list_min)
    print('Max:',list_max)
    print('Mean:',list_mean)
    print('Std:',list_std)
    print('Var:',list_variance)

result_stats('board0-raw.json')
result_stats('board1-raw.json')
