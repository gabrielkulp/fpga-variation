#!/usr/bin/env python3

import statistics
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

def get_zscore(x,mean,std):
    z=(x-mean)/std
    return z

def img_show(bel_means,mean,std,zscore=True):
    img=np.zeros((30,22),dtype=float)
    x=0
    y=0
    for b in bel_means:
        #x and y swapped for graph
        if zscore:
            img[y,x]=get_zscore(b,mean,std)
        else:
            img[y,x]=b**2
        y+=1
        if 30==y:
            x+=1
            y=0
    new_img=np.zeros((30,24),dtype=float)
    new_img[:,0:5]=img[:,0:5]
    new_img[:,6:19]=img[:,5:18]
    new_img[:,20:]=img[:,18:]
    graph=plt.imshow(new_img,interpolation='None',origin='lower')
    graph_colorbar=plt.colorbar(graph)
    if zscore:
        graph_colorbar.set_label('Z-Score')
    else:
        graph_colorbar.set_label('MHz difference between BELs')
    if zscore:
        plt.title('iCEBreaker FPGA BEL Variance', fontsize=12)
    else:
        plt.title('iCEBreaker Board Comparision', fontsize=12)
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
    list_mean=statistics.mean(results_list)
    list_std=statistics.stdev(results_list,list_mean)
    list_variance=statistics.variance(results_list,list_mean)

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

    return results_panda,results_list

def difference(rp0,rl0,rp1,rl1):
    complete_list=rl0+rl1
    complete_list.sort()
    complete_mean=statistics.mean(complete_list)
    complete_std=statistics.stdev(complete_list,complete_mean)
    complete_var=statistics.variance(complete_list,complete_mean)
    diff_rp=rp0-rp1
    diff_mean=diff_rp.mean()
    img_show(diff_mean,complete_mean,complete_std,zscore=False)
    print('Overall min:',complete_list[0])
    print('Overall max:',complete_list[len(complete_list)-1])
    print('Overall mean:',complete_mean)
    print('Overall std:',complete_std)
    print('Overall var:',complete_var)

def stats(file0,file1):
    rp0,rl0=result_stats(file0)
    rp1,rl1=result_stats(file1)
    difference(rp0,rl0,rp1,rl1)


stats('board0-raw.json','board1-raw.json')