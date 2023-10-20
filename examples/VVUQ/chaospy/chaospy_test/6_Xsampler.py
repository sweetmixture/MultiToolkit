#!/bin/bash

import os,sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import chaospy as cp

scale1 = 6
sigma1 = 0.01
d = cp.Normal(0.5, sigma1)
# Generate 100 samples
samples1 = d.sample(10000, rule='random')		# 'samples' -> numpy array
#samples1 = samples1*scale1 + scale2*0.5 - scale1*0.5 #3


scale2 = scale1 * 2.
#sigma2 = 0.01
sigma2 = sigma1 / 2.

samples1 = samples1*scale1 + scale2*0.5 - scale1*0.5 #3

d = cp.Normal(0.5, sigma2)
samples2 = d.sample(10000, rule='random')		# 'samples' -> numpy array
samples2 = samples2*scale2

fig, axes = plt.subplots(1,2)

plt.subplots_adjust( wspace = 0.15,
        hspace = 0.15,
        left = 0.15,
        right = 0.95,
        bottom = 0.11,
        top = 0.95)

_div = 60
sns.histplot(data=samples1,bins=(len(samples1.tolist())//_div),kde=True,stat='probability',color='g',ax=axes[0])
sns.histplot(data=samples2,bins=(len(samples2.tolist())//_div),kde=True,stat='probability',color='r',ax=axes[1])

sns.histplot(data=samples2,bins=(len(samples2.tolist())//_div),kde=True,stat='probability',color='r',ax=axes[0])

plt.show()
