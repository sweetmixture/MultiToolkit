#!/bin/python

import sys,os
import numpy as np
import pandas as pd
import pickle

from tqdm import tqdm

from concurrent.futures import ProcessPoolExecutor
from Extractor.GULPstruct import GULPLattice

print(' * --------')
print(' ! RDF collection : 23-01-2024')
print(' * --------')
# input
try:
	size = sys.argv[1]
except:
	print('Err ... 1st arugment - size missed')
	sys.exit(1)

try:
	mode = sys.argv[2]
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
_smearing = 0.020

# using no smearing
cwd = os.getcwd()
csvfile = os.path.join(cwd,f'nconp{size}.csv')
df = pd.read_csv(csvfile)
#print(df)


# ----------------------------------- RDF setting (USERDEF)

'''
	Description
	
	* total 6 pairs

		(1) Mn Mn
		(2) Li Li	3,4
		(3) Tc Tc	5,6

		(4) Mn Li	7,8
		(5) Mn Tc	9,10
		(6) Li Tc	11,12
'''

pairlist = []
pair = ['Mn','Mn']
pairlist.append(pair)
pair = ['Li','Li']
pairlist.append(pair)
pair = ['Tc','Tc']
pairlist.append(pair)

pair = ['Mn','Li']
pairlist.append(pair)
pair = ['Mn','Tc']
pairlist.append(pair)
pair = ['Li','Tc']
pairlist.append(pair)
# ----------------------------------- RDF setting Done

# ------ task (rdf generation) mapping
for taskid in df['taskid'].tolist():

	tardir = 'A'+f'{taskid}'
	tardir = os.path.join(cwd,tardir)
	
	tarfile = os.path.join(tardir,'gulp_klmc.gout')
	
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
	glattice.set_lattice(tarfile)		# load tarfile (GULP output)

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
	glattice.set_lattice(tarfile)		# load tarfile (GULP output)

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

	with open(f'rdf{size}.pkl','wb') as f:
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
#	with open(f'rdf{size}.pkl','wb') as f:
#		pickle.dump(rdf_summary,f)

	with tqdm(total=len(tasklist), desc=' ! RDF generation', unit=' task') as pbar:

		with ProcessPoolExecutor(max_workers=int(os.cpu_count()/4)) as executor:

			for result in executor.map(rdf_process_parallel,tasklist):
	
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

				pbar.update(1)

	print(f' * ---')
	print(f' ! generation done')
	print(f' * ---')
	print(f' ! writing pkl : rdf{size}.pkl')
	print(f' * ---')

	with open(f'rdf{size}.pkl','wb') as f:
		pickle.dump(rdf_summary,f)

	print(f' ! finalising normally')

	'''
		! data access through pkl

		import pickle
		rdf_pkl = pickle.load(f)	# f: rdf{size}.pkl filepath

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









