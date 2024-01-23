#!/bin/python

import sys,os
import numpy as np
import pandas as pd
import pickle

from concurrent.futures import ProcessPoolExecutor

'''
	read-in files
'''

root = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell'

freq_file_root = []				# path to csvfile
csvlist = []				# csvfiles path

size = []
xlist = []

read_check = []				# check csv file exists
for i in range(25):
	file_path = os.path.join(root,f'li{i}')
	freq_file_root.append(os.path.join(root,f'fli{i}'))				# frequency calculation files root

	file_path = os.path.join(file_path,f'nconp{i}.csv')					# file path 'nconp{i}.csv'

	if not os.path.exists(file_path):
		print(file_path)
		print(f'file not found at: {file_path}',file=sys.stderr)
		sys.exit()

	csvlist.append(file_path)
	size.append(i)
	xlist.append(float(i)/24.)

print(' ! preparing csv files done')

# ---- Model Parameters
_e_gulp_mn2O4 = -534.25669638*6.                                        # R - Mn24O48 energy
_LiOx         = +5.39171                                                # Li(g) -> Li(+)(g) + e-
_MnRe         = -51.2                                                   # Mn(4+)(g) + e- -> Mn(3+)(g)
# this may change
_corr         = +1.6510 + 5.7400                                        # 1.6510(eV): formation energy Li CRC : +159.3kJ/mol Li(g), + residual energy 5.740 (eV)
# _corr = 7.391


'''
	read-in csv-files
'''
dflist = []			# include 'dataframe'(s) of generic GULP calculation result
freqlist = []		# include 'dict'(s) of GULP calculation frequencies



def task_process(arg):

	'''
		processing frequencies
		given taskid, read file and return taskid and frequencies
	'''
	taskid, file_path = arg

	freqlist = []
	with open(file_path,'r') as f:
		for line in f:
			freqlist.append(float(line.strip()))

	return taskid, freqlist

for csvfile,s in zip(csvlist,size):
	df = pd.read_csv(csvfile)

	# --- energy calibration in 'df'

	# --- energy calibration done
	dflist.append(df)

	#print(freq_file_root[s]) # checked

	#
	# --- read in gamma point frequencies
	#
	if s != 0:	# s : size

		freq_summary = {}	# save this into 'pkl'

		print(f'writing pkl for the size = {s} ...')

		# get taskid list
		taskid_list = df['taskid'].tolist()

		# taskid_path map object generation
		taskid_path_map = [] 
		for taskid in taskid_list:
			gulp_output_path = os.path.join(freq_file_root[s],f'A{taskid}')
			gulp_output_freq_path = os.path.join(gulp_output_path,'freq.out')

			taskid_path_map.append((taskid,gulp_output_freq_path))	# set map fpr PoolExecutor	- input 'taskid'/'freq.out file path'

		# dict
		freq_summary = {}
		with ProcessPoolExecutor(max_workers=32) as executor:
			for result in executor.map(task_process,taskid_path_map):
				freq_summary[result[0]] = result[1]
				# result[0] = taskid, result[1] = frequency_list

		with open(f'freq{s}.pkl','wb') as f:
			pickle.dump(freq_summary,f)
