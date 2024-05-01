#!/bin/python

import pickle
import sys,os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

def get_rdf(taskidlist,rdf_pkl,pairlist,output_csv):

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

	result_df = pd.DataFrame(result)
	result_df.to_csv(output_csv,index=False)

	return result	# json

# -----------------------------------------------------------------------------------------------

pairlist = ['CsCs','CsPb','CsI','PbPb','PbI','II']
pklfilelist = ['rdf1.pkl',  'rdf2.pkl',  'rdf3.pkl']
csvfilelist = ['Asubset1.csv',  'Asubset2.csv',  'Asubset3.csv']

# processing set 1
pkl_df = pd.read_pickle(pklfilelist[0])
csv_df = pd.read_csv(csvfilelist[0])
taskidlist = (csv_df['Unnamed: 0'] + 1).tolist()
rdfset1 = get_rdf(taskidlist,pkl_df,pairlist,'rdf_set1.csv')

# processing set 2
pkl_df = pd.read_pickle(pklfilelist[1])
csv_df = pd.read_csv(csvfilelist[1])
taskidlist = (csv_df['Unnamed: 0'] + 1).tolist()
rdfset2 = get_rdf(taskidlist,pkl_df,pairlist,'rdf_set2.csv')

# processing set 3
pkl_df = pd.read_pickle(pklfilelist[2])
csv_df = pd.read_csv(csvfilelist[2])
taskidlist = (csv_df['Unnamed: 0'] + 1).tolist()
rdfset3 = get_rdf(taskidlist,pkl_df,pairlist,'rdf_set3.csv')





# plotting
fig, axes = plt.subplots(1,6)

axes[0].plot(rdfset1['r'],rdfset1['CsCs'],color='red',label='set1 CsCs')
#axes[0].plot(rdfset2['r'],rdfset2['CsCs'],color='green')
axes[0].plot(rdfset3['r'],rdfset3['CsCs'],color='blue',linestyle='--')

axes[1].plot(rdfset1['r'],rdfset1['CsI'],color='red',label='set1 CsI')
#axes[1].plot(rdfset2['r'],rdfset2['CsI'],color='green')
axes[1].plot(rdfset3['r'],rdfset3['CsI'],color='blue',linestyle='--')

axes[2].plot(rdfset1['r'],rdfset1['CsPb'],color='red',label='set1 CsPb')
#axes[2].plot(rdfset2['r'],rdfset2['CsPb'],color='green')
axes[2].plot(rdfset3['r'],rdfset3['CsPb'],color='blue',linestyle='--')

axes[3].plot(rdfset1['r'],rdfset1['PbPb'],color='red',label='set1 PbPb')
#axes[3].plot(rdfset2['r'],rdfset2['PbPb'],color='green')
axes[3].plot(rdfset3['r'],rdfset3['PbPb'],color='blue',linestyle='--')

axes[4].plot(rdfset1['r'],rdfset1['PbI'],color='red',label='set1 PbI')
#axes[4].plot(rdfset2['r'],rdfset2['PbI'],color='green')
axes[4].plot(rdfset3['r'],rdfset3['PbI'],color='blue',linestyle='--')

axes[5].plot(rdfset1['r'],rdfset1['II'],color='red',label='set1 CsI')
#axes[5].plot(rdfset2['r'],rdfset2['II'],color='green')
axes[5].plot(rdfset3['r'],rdfset3['II'],color='blue',linestyle='--')

# plotting
fig, axes = plt.subplots(1,2)

axes[0].plot(rdfset1['r'],rdfset1['CsI'],color='red',label='set1 CsI')
axes[0].plot(rdfset3['r'],rdfset3['CsI'],color='blue',linestyle='--')

axes[1].plot(rdfset1['r'],rdfset1['PbI'],color='red',label='set1 PbI')
axes[1].plot(rdfset3['r'],rdfset3['PbI'],color='blue',linestyle='--')

for i in range(2):
    if i == 0:
        axes[i].set_ylabel(f'RDF (a.u.)')
axes[0].set_xlabel('Distance Cs-I ($\AA$)')
axes[1].set_xlabel('Distance Pb-I  ($\AA$)')

axes[0].set_xlim(3.7,4.0)
axes[1].set_xlim(6.3,6.7)

fig.set_size_inches((20,7))
plt.subplots_adjust( wspace = 0.15,
        hspace = 0.15,
        left = 0.06,
        right = 0.95,
        bottom = 0.11,
        top = 0.95)
#plt.plot(r,grdf,label=target_pair,color='green')
#plt.legend()
plt.savefig(f'rdf_total_selected.png',bbox_inches='tight')
plt.show()
#sys.exit(1)


