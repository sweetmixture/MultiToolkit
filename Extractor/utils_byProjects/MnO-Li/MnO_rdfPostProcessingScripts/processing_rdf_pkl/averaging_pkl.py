#!/bin/python

import pickle
import sys,os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

try:
	pklfile = sys.argv[1]
	csvfile = sys.argv[2]
	target_pair = sys.argv[3]
	size = int(sys.argv[4])
except:
	print(' * Err ... one of following inputs missed')
	print('(1) pklfile\n(2) csvfile\n(3) target_pair : LiLi, LiTc, TcTc\n(4) size')

	sys.exit(1)

# load pkl
#with open(pklfile,'rb') as f:
#    rpkl = pickle.load(f)
pkl_df = pd.read_pickle(pklfile)
csv_df = pd.read_csv(csvfile)

taskidlist = csv_df['taskid'].tolist()


r = None
rdf = None
#
# prepare empty 
#
for i,taskid in enumerate(taskidlist):
	rdf_sample = pkl_df[taskid]
	r = np.array(rdf_sample['r']).tolist()
	rdf = np.array(rdf_sample[target_pair]).tolist()
	break

r   = np.array([ 0. for i in range(len(r))])
rdf = np.array([ 0. for i in range(len(rdf))])

for i,taskid in enumerate(taskidlist):

	rdf_sample = pkl_df[taskid]

	r = r + np.array(rdf_sample['r'])
	rdf = rdf + np.array(rdf_sample[target_pair])

# finalising
r = r/float(len(taskidlist))
rdf = rdf/float(len(taskidlist))
sigma = 1.0
#grdf = gaussian_filter1d(rdf,sigma=sigma)
grdf = rdf

plt.plot(r,grdf,label=target_pair,color='green')

plt.legend()
plt.savefig(f'ave_rdf_{size}_{target_pair}.png',bbox_inches='tight')
#plt.show()

