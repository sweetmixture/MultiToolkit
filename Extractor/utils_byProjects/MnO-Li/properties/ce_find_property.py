#!/bin/python

import os,sys
import pandas as pd
import numpy as np
import pickle

import time
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

# from concurrent.futures import ProcessPoolExecutor

# constants ----
_wavenumber_to_ev = np.float128(1.239841984332e-4)
_kb = np.float128(8.617333262e-5)

#
# internal use functions	-----------------------------------------------------
#
def expkbt(E,T):

	global _kb
	#E = np.float128(E)
	#T = np.float128(T)

	#try:
	#	ret = np.exp(-E/T/_kb)
	#except OverflowError:
	#	if -E/T/_kb > 500:
	#		ret = np.exp(500.)

	ret = np.exp(-E/T/_kb)
	return ret

def expkbt_obs(E,T,O):

	global _kb
	ret = np.float128(0.)
	E = np.float128(E)
	T = np.float128(T)

	ret = O * np.exp(-E/T/_kb)

	return ret

'''
	calculating G(x,T), Z(x,T)

	x : model variable (Li concentration)
	T : temperature
'''

def get_gz(csvdf,T,vib=False,pkldf=None):

	global _kb
	global _wavenumber_to_ev
	#u = np.float128(0.)	# _corr

	Elist = csvdf['energy'].values
	Egm = np.float128(Elist[0])		# global minimum

	T = np.float128(T)
	Z = np.float128(0.)
	G = np.float128(0.)

	if vib == False:

		for E in Elist:
			E = np.float128(E) - Egm
			Z += expkbt(E,T)
		
		Z = np.exp(-Egm/_kb/T) * Z	
		G = - _kb * T * np.log(Z)
		#print(Egm,-Egm/_kb/T,np.exp(-Egm/_kb/T),Z,G)
	#
	# include vibrational contributions
	#
	elif vib == True:
		#
		# looping thru structures / distinguished by 'taskid'
		#
		for E,taskid in zip(Elist,csvdf['taskid'].values):

			E = np.float128(E) - Egm
			ZE = expkbt(E,T)

			#
			# get freq info for this struct
			#
			freqlist = np.array(pkldf[taskid],dtype=np.float128)
			# add ZPE contribution - gamma point ?
			freq0_power = np.float128(0.)
			for freq in freqlist:
				freq0_power += (0.5 * freq * _wavenumber_to_ev)	
			Zvib0 = np.exp(-freq0_power/_kb/T)
	
			# add all vib contribution
			# NotImplemented

			# sum up
			Z += (ZE * Zvib0)

		# pull back Egm
		Z = np.exp(-Egm/_kb/T) * Z
		G = - _kb * T * np.log(Z)

	return np.float128(G),np.float128(Z)


#
# GCE Added !
def get_wx(npZlist,npxlist,u,T):

	global _kb
	
	u = np.float128(u)
	wxlist = []	# return tmp

	for Z,x in zip(npZlist,npxlist):
		
		Zg = np.float128(0.)
		for Zp,xp in zip(npZlist,npxlist):
			Zg = Zg + np.exp((xp-x)*u/_kb/T) * Zp

		wx = Z/Zg
		wxlist.append(wx)

	return np.array(wxlist,dtype=np.float128)	# final type np.float128 numpy array

def get_expect_x(npxlist,npwxlist):

	expect_x = np.float128(0.)
	for x,wx in zip(npxlist,npwxlist):
		expect_x = expect_x + x*wx
	return expect_x

def get_grand_z(npZlist,npxlist,u,T):

	global _kb

	u = np.float128(u)
	Zg = np.float128(0.)

	# summation over 'x'
	for Z,x in zip(npZlist,npxlist):
		Zg = Zg + np.exp(x*u/_kb/T) * Z

	return Zg
#
# inverting function <x>(u) ---> u(<x>)
#
def get_u_by_x_acc(x,xlist,ulist):	# accurate version returning actual (x,u) and request x

	'''
		input x (requested x)

		return closest 'u' value

		xlist -> expect_xlist
		ulist -> ulist
	'''

	if len(xlist) != len(ulist):
		print(f'Err, xlist / ulist length are different ... something is wrong')
		sys.exit(1)
	if x < 0.0001 or x > 1.0:
		print(f'Err, x value must be in range [0.0001:1.0000]')
		sys.exit(1)

	# closest index (ci)
	ci = min(range(len(xlist)), key=lambda i: abs(xlist[i] - x))

	requested_x = x
	return_x = xlist[ci]
	return_u = ulist[ci]

	return requested_x, return_x, return_u

	#return ulist[ci]

#
# GCE ---- function end ---- -------------------------------------------------------------------
#

# USER DEF
'''
	mode 1 : use n0 1000  samples
	mode 2 : use n0 5000  samples
	mode 3 : use n0 10000 samples
	mode 4 : use n0 100000samples -> extreme
'''
_mode = 3

freq_path =  f'/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/energy_pkl/x0_correction/freq{_mode}'
std_path = f'/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/energy_pkl/x0_correction/nconp{_mode}'

# custom functions

# load any pkl file
def load_pkl(pklfile):
	return pd.read_pickle(pklfile)


# ---------------- output

print(f' ! ------------------------------------------------------------------------')
print(f' ! canonical analysis RDF')
print(f' * freq_path pkl form			 : {freq_path}')
print(f' * std_path gulp_std_output(csv) : {std_path}')
print(f' ! Extrating info ...',flush=True)

freq_pkl_list = [ f'freq{i}.pkl' for i in range(25) ]		# DV - dummy variables
std_csv_list = [ f'nconp{i}.csv' for i in range(25) ]		# DV

freq_pkl_paths = [os.path.join(freq_path, item) for item in freq_pkl_list]
std_csv_paths = [os.path.join(std_path, item) for item in std_csv_list]

# ----------------- file check
fchecklist = []
for file in freq_pkl_paths:
	fchecklist.append(os.path.exists(file))
if False not in fchecklist:
	print(f' * freq_pkl file check done')
else:
	print(f' * freq_pkl file extracting failed')
	sys.exit(1)

fchecklist = []
for file in std_csv_paths:
	fchecklist.append(os.path.exists(file))
if False not in fchecklist:
	print(f' * std_csv	file check done')
else:
	print(f' * std_csv file extracting failed')
	sys.exit(1)
print(f' ! * * *',flush=True)

# ------------------- data loading
ct1 = time.time()

# Function to load CSV file
def load_csv(std):
	return pd.read_csv(std)

# Function to load pickle file
def load_pickle(freq_pkl):
	return pd.read_pickle(freq_pkl)

std_dflist = []
freq_dflist = []

# Parallelize loading of CSV files
print(f' ! starting at ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), flush=True)
print(f' ! reading in std_csv', end='')
with ProcessPoolExecutor() as executor:
	#futures_csv = [executor.submit(load_csv, std) for std in tqdm(std_csv_paths, desc="load gulp stdout csv", total=len(std_csv_paths))]
	futures_csv = [executor.submit(load_csv, std) for std in std_csv_paths]
	for future in tqdm(futures_csv, desc='Loading gulp stdout csv', total=len(std_csv_paths)):
		std_df = future.result()
		std_dflist.append(std_df)
print(f' - loading at ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), flush=True)
#for csv in std_dflist:
#	print(csv)

# Parallelize loading of pickle files for freq
print(f' ! starting at ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), flush=True)
print(f' ! reading in freq_pkl', end='')
with ProcessPoolExecutor() as executor:
	#futures_freq = [executor.submit(load_pickle, freq_pkl) for freq_pkl in tqdm(freq_pkl_paths, desc='load gulp freq pkl', total=len(freq_pkl_paths))]
	futures_freq = [executor.submit(load_pickle, freq_pkl) for freq_pkl in freq_pkl_paths]
	for future in tqdm(futures_freq, desc='Loading gulp freq pkl', total=len(freq_pkl_paths)):
		freq_df = future.result()
		freq_dflist.append(freq_df)
print(f' - loading at ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), flush=True)

ct2 = time.time()
load_et = ct2 - ct1
print(f' * loading elapsed time : {load_et} (s)',flush=True)
print(f' ! ------------------------------------------------------------------------')


#
# PREPARATION PHASE 1 - DROP IMAG FREQ SAMPLES
#
imlog = open("imag_freqlist.txt", "w") 
imlog.write(' * imag frequency listing [taskid]\n')

for i, (std_df,pkl_df) in enumerate(zip(std_dflist,freq_dflist)):		# 'i' is for file index !! not structure index

	taskid_list = std_df['taskid'].tolist()

	print(f' * processing size {i} | data count {len(std_df)} ...')
	_drop_cnt = 0
	imag_freqlist = []

	# 1st scan : looping imag freq
	for struct_no, taskid in enumerate(taskid_list):
	
		# get frequencies of a struct with 'taskid'
		freqlist = pkl_df[taskid]

		_isdropped = False

		for freq in freqlist:
			if freq < -0.5:
				imag_freqlist.append(taskid)

				std_df = std_df.drop(struct_no)
				_isdropped = True
				_drop_cnt = _drop_cnt + 1
				break

		if not _isdropped:
			pkl_df[taskid] = pkl_df[taskid][3:]
			
	imlog.write(f' * {_drop_cnt}/{len(taskid_list)} structures with imaginary frequencies were found : ')
	for imag_taskid in imag_freqlist:
		imlog.write(f' {imag_taskid},')
	imlog.write('\n')

	print(f' * {_drop_cnt}/{len(taskid_list)} structures with imaginary frequencies were found')
	print(f' ! finished')
	
	std_dflist[i] = std_df		# after dropping out imag freq taskids
	freq_dflist[i] = pkl_df		# after dropping out imag freq taskids -> here freq_dflist[i] is with trans/rota freqencies

imlog.close() # close imag freq log
#
#
# ------------------------ imag freq structure dropping finished


#
# PREPARATION PHASE 2 - Energy Recalibration
#

# some model parameters
_e_gulp_mn2O4 = -534.25669638*6.										# R - Mn24O48 energy - unitcell based -534.25669638
_LiOx		  = +5.39171												# Li(g) -> Li(+)(g) + e-
_MnRe		  = -51.2													# Mn(4+)(g) + e- -> Mn(3+)(g)
# this may change
_corr		  = +1.6510 + 5.7400										# 1.6510(eV): formation energy Li CRC : +159.3kJ/mol Li(g), + residual energy 5.740 (eV) # _corr = 7.391
# using sample count
_max_sample = 10000
sizelist = [ i for i in range(25) ]

# GCE Added !
npxlist = np.array([ float(i)/24. for i in range(25) ], dtype=np.float128)

tmp_csvlist = []		# processed csvlist
for s, std_df in zip(sizelist,std_dflist):

	if len(std_df) > 10000:
		#csvdf = csvdf.sample(n=_max_sample, random_state=42)	# use same randseed to keep reproducibility
		std_df = std_df.head(10000)

	# Lithiation Reaction Energy converting
	std_df['energy'] = (std_df['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.
	#std_df['energy'] = (std_df['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + 0. ) * s )/24. # no chemical potential
	std_df = std_df.sort_values(by='energy',ascending=True)

	print(f' * reaction energy calculation ... size : {s}')
	#print(std_df)
	tmp_csvlist.append(std_df)

std_dflist = tmp_csvlist

# ---- Setting Temperature
try:
	_T = np.float128(float(sys.argv[1]))
except:
	_T = np.float128(300.)
try:
	_vib_flag = sys.argv[2]
	if _vib_flag == '-vib':
		_include_vib = True
except:
	_include_vib = False

print(f' ! ------------------------------------------------------------------------')
print(f' * start ensemble analysis')
print(f' * temperature (K)	   = {_T}')
print(f' * including vibration = {_include_vib}')
print(f' ! ------------------------------------------------------------------------')

#
# G,Z =  def get_gz(csvdf,T,vib=False):
#
npGlist = np.zeros(len(std_dflist),dtype=np.float128)
npZlist = np.zeros(len(std_dflist),dtype=np.float128)

for s, (std_df,freq_df) in enumerate(zip(std_dflist,freq_dflist)):

	#print(f' * processing partition function Z : size {s}')
	Gc,Zc = get_gz(std_df,_T,vib=_include_vib,pkldf=freq_df)		# MUST INCLUDE VIB FOR X = 0 Otherwise -> ERRRRRORRRRR!!!
	npGlist[s] = Gc
	npZlist[s] = Zc

	#print(' ! size %.3d - [G,Z] : %20.12e%20.12e' % (s,npGlist[s],npZlist[s]))		# inf error in low T e.g., 10K
	print(f' ! size {s} - [G,Z] :',end='')
	print(npGlist[s],'\t',npZlist[s])

print(f' ! ------------------------------------------------------------------------')
print(f' * calculation of canonical G / Z done ...')
print(f' ! ------------------------------------------------------------------------')

'''
	* GCE analysis

	calculating averaged RDF as a function of (u,T)

	saved data --------- upto here

	G(x) : npGlist<list<np.float128>>
	Z(x) : npZlist<list<np.float128>>

	input	   ---------

	u : chemical potential
	T : temperature

	
	* Synopsis

		To provide observables at <x>(u,T) --> need to find the chemical potential at u(<x>,T) 

		<x> : GCE expected Li concentration
'''

print(f' * calculating <x> as a function of 'u' at given T : i.e., <x>(u,T)')

# chemical potential window

# x 100 times resoultion - c.f., voltage calculation
_bin = 300000
_rbin = _bin - 100000
_du = 0.000025

# x 10 times resoultion - c.f., voltage calculation
_bin = 30000
_rbin = _bin - 10000
_du = 0.00025

'''
	x 10 setting guarantees 10E-5 level accuracy on <x> -> u for 10K - 300K
'''

ulist = [ float(i) * _du for i in range(-_bin,_rbin+1) ]
#
current_time = time.time()
print(f' ! ------------------------------------------------------------------------')
print(f' ! chemical pontential configuration')
print(f' ! bin range   : {-_bin} ~ {_rbin}')
print(f' ! u window(eV): {-_bin*_du} ~ { _rbin*_du}')
print(f' ! delta u	   : {_du}')
print(f' ! ------------------------------------------------------------------------')
print(f' * obtaining particle distribution fuction & expected <x>')
print(f' ! starts  at : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time)))

# serial ----------------------------------------------------------------------------
#expect_xlist = []
#for i,u in enumerate(ulist):
#	print(f' ! working on : {i+1}/{len(ulist)}', end='\r')
#	npwxlist = get_wx(npZlist,npxlist,u,_T)
#	expect_x = get_expect_x(npxlist,npwxlist)
#	expect_xlist.append(expect_x)

# parallel --------------------------------------------------------------------------
# create task container : tasklist
tasklist = []
for k,u in enumerate(ulist):
	print(f" ! preparing ulist task : {k+1}/{len(ulist)}", end='\r')
	task_elem = (npZlist,npxlist,u,_T) 
	tasklist.append(task_elem)
print(f' * task preparation done')
# Define a function to compute expect_x for a given u
def compute_expect_x(arg):
	
	npZlist, npxlist, u, _T = arg

	npwxlist = get_wx(npZlist, npxlist, u, _T)
	return get_expect_x(npxlist, npwxlist)

expect_xlist = []
with tqdm(total=len(tasklist), desc=' ! <x>(u) generation', unit='task') as pbar:
	#with ProcessPoolExecutor(max_workers=64) as executor:								# 64 cpus may cause deadlock depending on the login-node status
	with ProcessPoolExecutor() as executor:
		for result in executor.map(compute_expect_x,tasklist):
			expect_xlist.append(result)
			pbar.update(1)

del tasklist
# parallel end ----------------------------------------------------------------------

#
# Writing u, x : for cell voltage profile in GCE level
#
with open(f'x_u_T{_T}.out','w') as f:
	
	f.write('%20s%20s%20s\n' % ('<x>','𝜇','-𝜇'))
	for x,u in zip(expect_xlist,ulist):
		f.write('%20.12e%20.12e%20.12e\n' % (x,u,-u))

new_time = time.time()
print(f' ! ends   at  : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_time)))
print(f' ! elapsed t  : {new_time - current_time}')
print(f' ! ------------------------------------------------------------------------')
print(f' * <x>(u,T) inverting .... --> u(<x>,T)')
print(f' ! ------------------------------------------------------------------------')

# setting <x> bin
_xbin = 2000
_dx   = 1./_xbin
ixlist = [ float(i) * _dx for i in range(1,_xbin+1) ]
npixlist = np.array(ixlist,dtype=np.float128)

current_time = time.time()
print(f' ! <x> configuration')
print(f' ! bin range : 1 ~ {_xbin}') 
print(f' ! x window  : {_dx} ~ {_dx*_xbin}')
print(f' ! delta x	 : {_dx}')
print(f' ! ------------------------------------------------------------------------')
print(f' * obtaining inverted u(<x>,T)') 
print(f' ! starts  at : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time)))

# test accuracy
x_samplelist = [ 0.1*float(i+1) for i in range(10) ]
print(f' * inversion check -> compare to values in x_u_T{_T}.out file')
for x in x_samplelist:
	rx, ax, u = get_u_by_x_acc(x,expect_xlist,ulist)

	Zg = get_grand_z(npZlist,npxlist,u,_T)

	print(f' | rx, ax, u : %20.12e%20.12e%20.12e | err_in_x %20.12e | Zg : ' % (rx,ax,u,(ax-rx)), end='')
	print(Zg)
	#print(f' | rx, ax, u, Zg : %20.12e%20.12e%20.12e%20.12e | err_in_x %20.12e' % (rx,ax,u,Zg,(ax-rx)))		# inf error on Zg printing - only formatted printing error

new_time = time.time()
print(f' ! ends   at  : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_time)))
print(f' ! elapsed t  : {new_time - current_time}')
print(f' ! ------------------------------------------------------------------------')

# upto here finding voltage curves
# end after printing x, u, -u ------------------------------------------------------------------------------------------

#
# Perform RDF Grand Canonical analysis
#
#  use : rx, x, u = get_u_by_x_acc(x,expect_xlist,ulist) -> to get chemical potential for a Li concentration <x>
#				^^				   ^
#  chemical potential	<x> Li concentration
#
#  rx : requested <x> / ax : actual <x> for corresponding 'u'
#
#  prepared data set:
#  expect_xlist
#  ulist
#

task_type = 'Property'
print(f' ! Ensemble Averaging ... task : {task_type}')
gce_start_t = time.time()
print(f' ! starts  at : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(gce_start_t)))
print(f' ! ------------------------------------------------------------------------')
# USER
proplist = ['a','b','c','alp','bet','gam','vol']
print(f' ! Requested properties: ', end='')
for prop in proplist:
	print(f'{prop}, ',end='')
print(f'')

#
# GCE constants
#
# need list of <x> and corresponding chemical potentials 'ulist'

#
# prepare gce_prop saving place - prop_ce_ints(values)
#
# saved seperately for each size 'i' as noted below
#
prop_ce_ints = [ {} for i in range(len(sizelist)) ]
for i in range(len(prop_ce_ints)):
	for prop in proplist:
		prop_ce_ints[i][prop] = 0.		# reset property 
#
# outer loop : iterating 'x' (or size)
#
for size_x, (std_df,xp) in enumerate(zip(std_dflist,npxlist)):

	size_start_t = time.time()

	print(f' * processing {size_x} properties ...')

	# for 'size_x' get sample energy list
	Elist = std_df['energy'].values
	# for 'size_x' get sample global minimum energy
	Egm = np.float128(Elist[0])	
	# for 'size_x' get sample-taskid identifier
	taskidlist = std_df['taskid'].values

	# for 'size_x' get sample properties
	Plist = []
	for prop in proplist:
		Plist.append(std_df[prop].values)

	if _include_vib == False:
		#
		# looping samples for 'size_x' : s(sample)
		#
		for s, (Es,taskid) in enumerate(zip(Elist,taskidlist)):

			print(f" ! working on : {s+1}/{len(taskidlist)}", end='\r')

			# get sample energy
			Es = np.float128(Es) - Egm

			#
			# looping properties
			#
			for k,prop in enumerate(proplist):

				prop_ce_ints[size_x][prop] += np.float128(Plist[k][s]) * expkbt(Es,_T)

	if _include_vib == True:
		#
		# looping samples for 'size_x' : s(sample)
		#
		for s, (Es,taskid) in enumerate(zip(Elist,taskidlist)):

			print(f" ! working on : {s+1}/{len(taskidlist)}", end='\r')

			#
			# get sample energy
			Es = np.float128(Es) - Egm

			#
			# get sample freq
			freqlist = np.array(freq_dflist[size_x][taskid],dtype=np.float128)

			ZPEs = np.float128(0.)
			for freq in freqlist:
				ZPEs += (0.5 * freq * _wavenumber_to_ev)

			# add ZPE correction to the sample energy
			Es = Es + ZPEs

			#
			# looping properties
			#
			for k,prop in enumerate(proplist):

				prop_ce_ints[size_x][prop] += np.float128(Plist[k][s]) * expkbt(Es,_T)

	#
	# multiply exp(xu/kb/T) for all samples
	#
	for prop in proplist:
		prop_ce_ints_nptmp = np.array(prop_ce_ints[size_x][prop]) * np.exp(-Egm/_kb/_T) 
		prop_ce_ints[size_x][prop] = prop_ce_ints_nptmp

	size_end_t = time.time()

	print(f' ! starts  at	: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(size_start_t)))
	print(f' ! ends    at	: ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(size_end_t)))
	print(f' ! time elapsed : {size_end_t - size_start_t}')
	print(f' * ---------------------------------------------------')

# ------------------------------------------
# CE property done
#
# prop in proplist
#
# saved in : prop_ce_ints[size][prop]
#	e.g., proplist = ['a','b','c','alp','bet','gam','vol']
# ------------------------------------------

#
# writing CE averaged result
with open(f'PROP_CE_{_T}.prop','w') as f:

	for prop in proplist:
		f.write('%20s' % (prop))
	f.write('\n')

	for size_x in sizelist:

		f.write('%20.12e' % (float(size_x/24.)))

		for prop in proplist:
			f.write('%20.12e' % (prop_ce_ints[size_x][prop] / npZlist[size_x]))
		f.write('\n')

sys.exit()
#
# after obtaining CE rdf - summing up for GCE
#
# & writing GCE averaged result (u,T)
rxlist = [ 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0 ]

for _x in rxlist:

	#_x = 0.1
	_rx, _ax, _u = get_u_by_x_acc(_x,expect_xlist,ulist)
	_zg = get_grand_z(npZlist,npxlist,_u,_T)
	
	rdf_gce_ints = {}
	for pair in pairlist:
		rdf_gce_ints[pair] = np.array([ np.float128(0.) for i in range(len(rdf_r)) ])
	
	for size_x, xp in enumerate(npxlist):
	
		for pair in pairlist:
	
			rdf_gce_ints[pair] += (rdf_ce_ints[size_x][pair] * np.exp( xp * _u /_kb/_T ) / _zg)
	
	# writing
	with open(f'RDF_GCE_{_T}_{_rx}.rdf','w') as f:
	
		f.write(f'rx={_rx} ax={_ax} u={_u}\n')
		# rx : requested 'x'
		# ax : acutal 'x'
		# u  : corresponding chemical potential for 'ax'
	
		for i,r in enumerate(rdf_r):
	
			f.write('%20.12e' % (r))
			for pair in pairlist:
				f.write('%20.12e' % (rdf_gce_ints[pair][i]))
			f.write('\n')



# GCE end ------------------------------------------------------------------------
sys.exit()

