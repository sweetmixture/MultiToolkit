#!/bin/bash

import os,sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import math
import chaospy as cp

# fractional coordinate
fc = 0.5
# scaling factor
f = 1./math.sqrt(2.)

scale1 = 12	# 12 original lattice: lattice constant 1
sigma1 = 0.01
d1 = cp.Normal(fc, sigma1)
samples1 = d1.sample(10000, rule='random')		# 'samples' -> numpy array
#samples1 = samples1*scale1 + scale2/fc - scale1/fc


scale2 = scale1*f	# scale1 (org lattice) * f scaling factor -> lattice constant 2
sigma2 = sigma1/f
'''
	if lattice shrink : i.e. 0 < f < 1 or scale2 < scale1

		sigma2 must increase

		-> sigma2 = sigma2 / f
'''

# shifting : sample 1 centre position - for comparison purpose
samples1 = samples1*scale1 + scale2*fc - scale1*fc

d2 = cp.Normal(fc, sigma2)
samples2 = d2.sample(10000, rule='random')		# 'samples' -> numpy array
samples2 = samples2*scale2

fig, axes = plt.subplots(1,2)

plt.subplots_adjust( wspace = 0.15,
        hspace = 0.15,
        left = 0.15,
        right = 0.95,
        bottom = 0.11,
        top = 0.95)

_div = 60
sns.histplot(data=samples1,bins=(len(samples1.tolist())//_div),kde=True,stat='probability',color='g',ax=axes[0])	# green scale - 12
sns.histplot(data=samples2,bins=(len(samples2.tolist())//_div),kde=True,stat='probability',color='r',ax=axes[1])	# red   scale - 12 * (1/sqrt(2))

sns.histplot(data=samples2,bins=(len(samples2.tolist())//_div),kde=True,stat='probability',color='r',ax=axes[0])

plt.show()
