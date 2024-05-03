#!/bin/python3

import pandas as pd
import sys

'''
	increasing number of x=0 samples
'''

_def_csv = 'nconp0.csv'
_dup_max = int(sys.argv[1])

df = pd.read_csv(_def_csv)

# duplicate '_dup_max' times
df_dup = pd.concat([df]*_dup_max, ignore_index=True)

# reset taskid
for i in range(_dup_max):
	df_dup.loc[i,'taskid'] = i

#taskidlist = df_dup['taskid']
#for item in taskidlist:
#	print(item)

df_dup.to_csv(f'{_def_csv}.duplicate_{_dup_max}')
