#!/bin/bash

import os,sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import chaospy as cp

scale1 = 12
sigma1 = 0.01

d = cp.Normal(0.5, sigma1)
# Generate 100 samples
samples1 = d.sample(10000, rule='random')		# 'samples' -> numpy array
samples1 = samples1*scale1

fig, axes = plt.subplots(1,1)

plt.subplots_adjust( wspace = 0.15,
        hspace = 0.15,
        left = 0.15,
        right = 0.95,
        bottom = 0.11,
        top = 0.95)

_div = 60
sns.histplot(data=samples1,bins=(len(samples1.tolist())//_div),kde=True,stat='probability',color='g',ax=axes)

plt.show()
