#!/bin/python

import sys,os
import pandas as pd

# USER
df = pd.read_csv(sys.argv[1])	# sys.argv[1] must be the original 'csv' collection file from the previous final taskfarming run

print(df['taskid'])

dir_path = os.getcwd()

# USER
with open(f'freq{sys.argv[2]}.txt','w') as wf:

	total_len = len(df['taskid'].tolist())

	for cnt, taskid in enumerate(df['taskid'].tolist()):
	
		gdir  = 'A' + str(taskid)
		gpath = os.path.join(dir_path,gdir)
		gfile = 'freq.out'
		gpath = os.path.join(gpath,gfile)
	
		#print(os.path.exists(gpath),gpath)
		print(f'progressing {taskid} : {cnt}/{total_len}')

		f = open(gpath)
		freq_list = [ line.rstrip() for line in f.readlines() ]

		wf.write('%8.5s\t' % (taskid))
		for freq in freq_list:
			wf.write('%s\t' % (freq))
		wf.write('\n')
