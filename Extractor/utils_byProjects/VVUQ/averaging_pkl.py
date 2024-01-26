#!/bin/python

import pickle
import sys,os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

if sys.argv[1] == '-help':
	print('(1) pklfile\n(2) csvfile\n(3) target_pair : CsCs, PbPb, II, CsI, CsPb, PbI\n(4) tarset')
	sys.exit(1)

try:
	pklfile = sys.argv[1]
	csvfile = sys.argv[2]
	target_pair = sys.argv[3]	# CsCs PbPb II CsI CsPb PbI
	tarset = int(sys.argv[4]) #csvfile
except:
	print(' * Err ... one of following inputs missed')
	print('(1) pklfile\n(2) csvfile\n(3) target_pair : CsCs, PbPb, II, CsI, CsPb, PbI\n(4) tarset')

	sys.exit(1)

# load pkl
#with open(pklfile,'rb') as f:
#    rpkl = pickle.load(f)
pkl_df = pd.read_pickle(pklfile)
csv_df = pd.read_csv(csvfile)

#taskidlist = csv_df['taskid'].tolist()
taskidlist = (csv_df['Unnamed: 0'] + 1).tolist()


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
#sigma = 1.0
#grdf = gaussian_filter1d(rdf,sigma=sigma)
grdf = rdf

plt.plot(r,grdf,label=target_pair,color='green')

plt.legend()
plt.savefig(f'ave_rdf_{tarset}_{target_pair}.png',bbox_inches='tight')
#plt.show()

#sys.exit(1)

pairlist = ['CsCs','CsPb','CsI','PbPb','PbI','II']
def get_rdf(tasklist,rdf_pkl,pairlist):

	result = {}
	
	# get 'r'
	for i, taskid in enumerate(taskidlist):
		rdf_sample = rdf_pkl[taskid]
		r = np.array(rdf_sample['r']).tolist()
		rdf = np.array(rdf_sample[pairlist[0]]).tolist()
		break

	#r   = np.array([ 0. for i in range(len(r))])
	#rdf = np.array([ 0. for i in range(len(rdf))])
	result['r'] = r
	rdf_len = len(rdf)

	pair_rdf_list = [ np.array([ 0. for i in range(rdf_len)]) for i in range(len(pairlist)) ]

	for i,pair in enumerate(pairlist):

		for taskid in taskidlist:
			rdf_sample = rdf_pkl[taskid]
			pair_rdf_list[i] = pair_rdf_list[i] + np.array(rdf_sample[pair])

		pair_rdf_list[i] = pair_rdf_list[i]/float(len(taskidlist))

		result[pair] = pair_rdf_list[i]

	df.to_csv('output.csv',index=False)
