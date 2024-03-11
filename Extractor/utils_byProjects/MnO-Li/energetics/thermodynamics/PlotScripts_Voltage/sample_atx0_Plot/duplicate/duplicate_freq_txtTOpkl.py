#!/bin/python
import pickle, sys

# read freq file in 'txt' and duplicate then write in 'pkl' format

taskidlist = []
freqlist = []

_dup_max = int(sys.argv[1])

freq_summary = {}
with open(f'freq0.txt','r') as f:
	for line in f:

		ls = line.split()

		taskid = int(ls[0])
		freqlist = [ float(item) for item in ls[1:] ]
	
		#freq_summary[taskid] = freqlist

	# repeating _dup_max times for the same freqlist
	for i in range(_dup_max):

		freq_summary[i] = freqlist


with open(f'freq0.pkl.duplicate_{_dup_max}','wb') as f:
	pickle.dump(freq_summary,f)
