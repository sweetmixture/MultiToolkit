#!/bin/python

import sys,os
import numpy as np
import pandas as pd
import pickle

from tqdm import tqdm

from concurrent.futures import ProcessPoolExecutor
from Extractor.GULPstruct import GULPLattice

'''
	require 2 essential inputs

	(1) tarset : integer for writing output pkl format file, including rdf information
	(2) csvfile: including information of taskid and fhiaims geometry file to generate rdf

		from this csvfile, including summarised output from VVUQ-FHIaims runs, taskid may be missing, therefore a user must be carefule to use this script.

		at the moment, it uses

			taskidlist = (df['Unnamed: 0']+1).tolist()

		python command to extract correct ${taskid} / e.g., ${taskid}_aims.in.rotate / ${taskid}_aims_final.in / etc.

'''

print(' * --------')
print(' ! RDF collection : 23-01-2024')
print(' * --------')
# input
try:
	tarset = sys.argv[1]			# stringg
	taskid_src = sys.argv[2]		# csvfile
except:
	print('Err ... 1st arugment - tarset missed')
	sys.exit(1)

try:
	mode = sys.argv[3]
except:
	mode = '-serial'

if mode == '-parallel':
	print(f' * rdf generation mode : {mode}')
else:
	mode == '-serial'
	print(f' * rdf generation mode : {mode}')

#
# using variables
#

# df		(param)	: 'nconp{i}.csv'
# cwd		(param)	: 
# tasklist	(input) : map list
tasklist = []
# _smearing (global): gaussain smearing
_smearing = 0.001

# using no smearing
cwd = os.getcwd()
csvfile = os.path.join(cwd,taskid_src)
df = pd.read_csv(csvfile)
#print(df)

# REQUIRE :  tarset arguemnts !!!

# ----------------------------------- RDF setting (USERDEF)

'''
	Description
	
	* total 6 pairs

'''

pairlist = []
pair = ['Cs','Cs']
pairlist.append(pair)
pair = ['Pb','Pb']
pairlist.append(pair)
pair = ['I','I']
pairlist.append(pair)

pair = ['Cs','I']
pairlist.append(pair)
pair = ['Cs','Pb']
pairlist.append(pair)
pair = ['Pb','I']
pairlist.append(pair)
# ----------------------------------- RDF setting Done

# ------ task (rdf generation) mapping

taskidlist = (df['Unnamed: 0']+1).tolist()
print(taskidlist)
#for i,taskidlist in enumerate(taskidlist):
#	taskidlist[i] = taskidlist[i] + 1

for taskid in taskidlist:

	tardir = os.getcwd()
	
	tarfile = os.path.join(tardir,f'{taskid}_aims_final.in')
	
	#
	# Create process map : 
	#
	tasklist_elem = (taskid,tarfile,pairlist)
	tasklist.append(tasklist_elem)

print(' * ---')
print(' ! task mapping done ...')
print(' * ---')

# ---- RDF generation process

def rdf_process(arg):
	taskid, tarfile, pairlist = arg

	glattice = GULPLattice()			# create GULPLattice objcect
	glattice.set_lattice(tarfile,filetype='aims')		# load tarfile (GULP output)

	rlist = []
	rdflist = []

	global _smearing

	for pair in pairlist:

		r, rdf = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)	

		rlist.append(r)
		rdflist.append(rdf)

	return taskid, rlist, rdflist

def rdf_process_parallel(arg):
	taskid, tarfile, pairlist = arg

	glattice = GULPLattice()			# create GULPLattice objcect
	glattice.set_lattice(tarfile,filetype='aims')		# load tarfile (GULP output)

	rlist = []
	rdflist = []

	global _smearing

	for pair in pairlist:

		r, rdf = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)	

		rlist.append(r)
		rdflist.append(rdf)

	#print(f'\r progressing ... {taskid}',end='')	# replaced to tqdm
	return taskid, rlist, rdflist

#
# serial execution
#

if mode == '-serial':
	rdf_summary = {}
	for i,taskmap in enumerate(tasklist):
	
		result = rdf_process(taskmap)
		'''
			result[0]		: taskid
			result[1][]		: r
			result[2][]		: rdf
		'''
		
		rdf_element = {}
		# --------- USER DEF
		rdf_element['r'] = result[1][0]
		rdf_element['MnMn'] = result[2][0]
		rdf_element['LiLi'] = result[2][1]
		rdf_element['TcTc'] = result[2][2]
		rdf_element['MnLi'] = result[2][3]
		rdf_element['MnTc'] = result[2][4]
		rdf_element['LiTc'] = result[2][5]
		# --------- USER DEF
	
		rdf_summary[result[0]] = rdf_element
		#           ^^^^^^^^^    ^^^^^^^^^^^^
		#           taskid       rdf-data in dic format

		print(f'\r * progressing ... {i+1}/{len(tasklist)}',end='')
	print('')

	with open(f'rdf{tarset}.pkl','wb') as f:
		pickel.dump(rdf_summary,f)

if mode == '-parallel':

	rdf_summary = {}
	#with ProcessPoolExecutor(max_workers=32) as executor:	# on ARCHER2
	#with ProcessPoolExecutor(max_workers=int(os.cpu_count()/4)) as executor: # generic?
	#with ProcessPoolExecutor() as executor:
#	with ProcessPoolExecutor(max_workers=int(os.cpu_count()/4)) as executor: # generic?
#
#		for result in executor.map(rdf_process_parallel,tasklist):
#
#			rdf_element = {}
#			# --------- USER DEF
#			rdf_element['r'] = result[1][0]
#			rdf_element['MnMn'] = result[2][0]
#			rdf_element['LiLi'] = result[2][1]
#			rdf_element['TcTc'] = result[2][2]
#			rdf_element['MnLi'] = result[2][3]
#			rdf_element['MnTc'] = result[2][4]
#			rdf_element['LiTc'] = result[2][5]
#			# --------- USER DEF
#			
#			rdf_summary[result[0]] = rdf_element
#			#           ^^^^^^^^^    ^^^^^^^^^^^^
#			#           taskid       rdf-data in dic format
#
#	with open(f'rdf{set}.pkl','wb') as f:
#		pickle.dump(rdf_summary,f)

	with tqdm(total=len(tasklist), desc=' ! RDF generation', unit=' task') as pbar:

		with ProcessPoolExecutor(max_workers=int(os.cpu_count()/4)) as executor:

			for result in executor.map(rdf_process_parallel,tasklist):
	
				rdf_element = {}
				# --------- USER DEF
				rdf_element['r'] = result[1][0]
				rdf_element['CsCs'] = result[2][0]
				rdf_element['PbPb'] = result[2][1]
				rdf_element['II'] = result[2][2]
				rdf_element['CsI'] = result[2][3]
				rdf_element['CsPb'] = result[2][4]
				rdf_element['PbI'] = result[2][5]
				# --------- USER DEF
				
				rdf_summary[result[0]] = rdf_element
				#           ^^^^^^^^^    ^^^^^^^^^^^^
				#           taskid       rdf-data in dic format

				pbar.update(1)

	print(f' * ---')
	print(f' ! generation done')
	print(f' * ---')
	print(f' ! writing pkl : rdf{tarset}.pkl')
	print(f' * ---')

	with open(f'rdf{tarset}.pkl','wb') as f:
		pickle.dump(rdf_summary,f)

	print(f' ! finalising normally')

	'''
		! data access through pkl

		import pickle
		rdf_pkl = pickle.load(f)	# f: rdf{tarset}.pkl filepath

		#
		# using 'taskid' to access rdf data
		#
			rdf_data = rdf_pkl[taskid]

			examples>

				r = rdf_data['r']	 : <list> r values
				r = rdf_data['MnMn'] : <list> rdf values of 'MnMn'

				...
	'''

sys.exit(1)









