#
#   03.2024 W.Jee 
#
#   KLMC Solid Solution: scripts for production phase
#
'''
    Xingfan Zhang, 12/2023
    Woongkyu Jee, 12/203

	* note that this code running must be followed after converting all gulp generated cif to standardised 'cif': see 'KLMC_convert_gulp_cif_to_standard.py'
'''


import sys,os
import numpy as np
import pandas as pd
import pickle

from tqdm import tqdm

import Dans_Diffraction as dif
from concurrent.futures import ProcessPoolExecutor

print(' * --------')
print(' ! XRD collection : 31-01-2024')
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

	print(' Err ... serial mode is not supported')
	sys.exit(1)

if mode == '-parallel':
	print(f' * xrd generation mode : {mode}')
else:
	mode == '-serial'
	print(f' * xrd generation mode : {mode}')

	print(' Err ... serial mode is not supported')
	sys.exit(1)

#
# using variables
#

# df		(param)	: 'nconp{i}.csv'
# cwd		(param)	: 
# tasklist	(input) : map list
tasklist = []

cwd = os.getcwd()
csvfile = os.path.join(cwd,f'nconp{size}.csv')
df = pd.read_csv(csvfile)
#print(df)

# REQUIRE : 'nconp*.csv' + size arguemnts !!!

# -----------------------------------  setting (USERDEF)

# target cif file
target_file = 'std.cif'
# global variables
_wavelength = 1.54059	# Cu Ka generator
_energy_kev = dif.fc.wave2energy(_wavelength)
_two_theta_min = 10
_two_theta_max = 90

# ------ task (xrd generation) mapping
for taskid in df['taskid'].tolist():

	tardir = 'A'+f'{taskid}'
	tardir = os.path.join(cwd,tardir)
	tarfile = os.path.join(tardir,target_file)
	
	#
	# Create process map : 
	#
	tasklist_elem = (taskid,tarfile)
	tasklist.append(tasklist_elem)

print(' * ---')
print(' ! task mapping done ...')
print(' * ---')

# ---- XRD generation process

def xrd_process_parallel(arg):

	global _energy_kev
	global _two_theta_min
	global _two_theta_max

	taskid, tarfile = arg

	xtl = dif.Crystal(tarfile)
	xtl.Scatter.setup_scatter(min_twotheta=_two_theta_min, max_twotheta=_two_theta_max,output=False)

	tt, ints, refl = xtl.Scatter.powder('x-ray', units='twotheta', energy_kev=_energy_kev, peak_width=0.01, backgroup=0)

	#
	#	tt: 2theta, ints: differaction intensity, refl: reflection index -> all numpy.ndarray
	#

	# normalise
	nfactor = np.linalg.norm(ints)
	ints = ints / nfactor

	# extracting all elements in the first dimension
	tt = tt[:].tolist()
	ints = ints[:].tolist()

	return taskid, tt, ints

if mode == '-parallel':

	xrd_summary = {}

	with tqdm(total=len(tasklist), desc=' ! XRD generation', unit=' task') as pbar:

		with ProcessPoolExecutor(max_workers=int(os.cpu_count()/4)) as executor:

			for result in executor.map(xrd_process_parallel,tasklist):
	
				xrd_element = {}
				# --------- USER DEF
				xrd_element['twotheta'] = result[1]
				xrd_element['intensity'] = result[2]
				# --------- USER DEF
				
				xrd_summary[result[0]] = xrd_element
				#           ^^^^^^^^^    ^^^^^^^^^^^^
				#           taskid       xrd-data in dic format

				pbar.update(1)

				'''
					overall :

					xrd_summary = { taskid<int> :
										{ 'twotheta'<str> : list<float>,
										  'intensity'<str>: list<float> },
									...
								  }
				'''	

	print(f' * ---')
	print(f' ! generation done')
	print(f' * ---')
	print(f' ! writing pkl : xrd{size}.pkl')
	print(f' * ---')

	with open(f'xrd{size}.pkl','wb') as f:
		pickle.dump(xrd_summary,f)

	print(f' ! finalising normally')

	'''
		! data access through pkl

		import pickle
		xrd_pkl = pickle.load(f)	# f: xrd{size}.pkl filepath

		#
		# using 'taskid' to access xrd data
		#
			xrd_data = xrd_pkl[taskid]

			examples>

				tt   = xrd_data['twotheta']    : <list> twotheta values
				ints = xrd_data['intensity']   : <list> intensity values of XRD at tt

				...
	'''

sys.exit(1)









