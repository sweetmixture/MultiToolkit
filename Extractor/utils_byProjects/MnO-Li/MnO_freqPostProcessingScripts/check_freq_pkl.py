#!/bin/python

import pickle
import sys
'''
	check frequency pkl file using 'taskid'
'''
# USER DEFINE ----
_pkl_filename = 'klmc_freq_summary.pkl'     # converted frequency pkl file
_taskid = 0                                 # which taskid you want to print?
# USER DEFINE ----


# ----------------------------------------------------

import pickle
import sys
taskid = _taskid

with open(f'{_pkl_filename}','rb') as f:
    freq_pkl = pickle.load(f)

# size 1 taskid 123
for freqs in freq_pkl[taskid]:
    print(freqs)

print(f'length : {len(freq_pkl)}')
