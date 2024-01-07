#!/bin/python

import sys,os
import numpy as np
import pandas as pd
import pickle

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

#
# parallelise this loop later
#
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
		#
		# parallelise this loop later
		#
		for i,row in df.iterrows():	# @ iterating rows
			#print(row['taskid'],row['energy'])		# how to access
			taskid = int(row['taskid'])
			gulp_output_path = os.path.join(freq_file_root[s],f'A{taskid}')			# gulp output dir path
			gulp_output_freq = os.path.join(gulp_output_path,'freq.out')		# gulp 'freq.out' path

			#print(gulp_output_path,gulp_output_freq) # checked

			freqs = []

			# open frequency file
			with open(gulp_output_freq,'r') as f:
				for line in f:
					freqs.append(float(line.strip()))

			freq_summary[taskid] = freqs

		with open(f'freq{s}.pkl','wb') as f:
			pickle.dump(freq_summary)

