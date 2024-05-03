#
#   03.2024 W.Jee 
#
#   KLMC Solid Solution: scripts for production phase
#
# ----------------------------------------------------------
#
#   * this script is extended version of 'KLMC_get_rdf_single.py', which generates 'rdf' for all structures calculated through KLMC3 task-farming interface
#   ㄴresult will be saved in 'pickle' binary format
#
#   * note that to execute this script, you must prepare summary csv file for a taskfarming run: see /MnO-Li/MnO_ProductionPhase_PostScripting/ShellConp/KLMC_PoolGulpEx.py
#   ㄴrdf simulation performs based on 'taskid' given in the csv file
#
#   * this script is for generating radial distribution function for desired pairs (user's choice) 
#     (only for a single gulp periodic standard output file)
#
#   * setting desired pairs to investigate is user's responsibility.
#   ㄴnote that user must set '_pairlist' variable below
#     ! in this example, using a few possible pairs in LiMnO2 where Tc represents reduced Mn: see line 19
#
#   * for extracting a specific rdf and do plot: see 'single_plot_rdf.py' in '/MnO_rdfPostProcessingScripts'
#
# USER DEFINE variables ----
_mode = '-parallel' # or '-serial' # either -parallel/-serial must be picked
_summary_csvfile = ''    # taskid information required from 'KLMC_PoolGulpEx.py' generated csv file
_gulp_klmc_tf_prefix = 'A' # klmc taskfarming gulp run directory prefix, e.g., A0, A1, A2, ... A9999.
_gulp_output_filename = 'gulp_klmc.gout'     # set gulp output file that you want to generate RDF
_smearing_factor = 0.02          # set gaussian smearing, or broadening factor for RDF peaks
_pairlist = [['Mn','Mn'], ['Li','Li'], ['Tc','Tc'], ['Mn','Li'], ['Mn','Tc'], ['Li','Tc']]    # example of pairs in LiMnO2
_output_rdf_filename = 'output_rdf.pkl'
'''
    ! data access through pkl
    import pickle
    rdf_pkl = pickle.load(f)    # f: output_rdf.pkl filepath
    #
    # using 'taskid' to access rdf data
    #
        rdf_data = rdf_pkl[taskid]
        examples>
            r = rdf_data['r']    : <list> r values
            r = rdf_data['MnMn'] : <list> rdf values of 'MnMn'
            ...
'''

# USER DEFINE varaibles ----

# ---------------------------------------------------------------------------------------------------
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
#try:
#	size = sys.argv[1]
#except:
#	print('Err ... 1st arugment - size missed')
#	sys.exit(1)
#
#try:
#	mode = sys.argv[2]
#except:
#	mode = '-serial'
#
#if mode == '-parallel':
#	print(f' * rdf generation mode : {mode}')
#else:
#	mode == '-serial'
#	print(f' * rdf generation mode : {mode}')

mode = _mode
summary_csvfile = _summary_csvfile
#
# using variables
#

# df		(param)	: 'nconp{i}.csv'
# cwd		(param)	: 
# tasklist	(input) : map list
tasklist = []
# _smearing (global): gaussain smearing
_smearing = _smearing_factor

# using no smearing
cwd = os.getcwd()
csvfile = os.path.join(cwd,f'{_summary_csvfile}')
df = pd.read_csv(csvfile)
#print(df)

# REQUIRE : 'nconp*.csv' + size arguemnts !!!

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
#pairlist = []
#pair = ['Mn','Mn']
#pairlist.append(pair)
#pair = ['Li','Li']
#pairlist.append(pair)
#pair = ['Tc','Tc']
#pairlist.append(pair)
#
#pair = ['Mn','Li']
#pairlist.append(pair)
#pair = ['Mn','Tc']
#pairlist.append(pair)
#pair = ['Li','Tc']
#pairlist.append(pair)
# pair list
pairlist = _pairlist
# ----------------------------------- RDF setting Done

# ------ task (rdf generation) mapping
for taskid in df['taskid'].tolist():

	tardir = f'{_gulp_klmc_tf_prefix}'+f'{taskid}'
	tardir = os.path.join(cwd,tardir)
	
	tarfile = os.path.join(tardir,f'{_gulp_output_filename}')
	
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

	with open(f'{_output_rdf_filename}','wb') as f:
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
	print(f' ! writing pkl : {_output_rdf_filename}')
	print(f' * ---')

	with open(f'{_output_rdf_filename}','wb') as f:
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









