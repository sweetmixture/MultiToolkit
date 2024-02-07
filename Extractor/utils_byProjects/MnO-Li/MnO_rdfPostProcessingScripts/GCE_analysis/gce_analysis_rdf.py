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

#
# inverting function <x>(u) ---> u(<x>)
#
def get_u_by_x(x,xlist,ulist):

	'''
		input x

		return closest 'u' value
	'''

	if len(xlist) != len(ulist):
		print(f'Err, xlist / ulist length are different ... something is wrong')
		sys.exit(1)
	if x < 0.0001 or x > 1.0:
		print(f'Err, x value must be in range [0.0001:1.0000]')
		sys.exit(1)
	# closest index (ci)
	ci = min(range(len(xlist)), key=lambda i: abs(xlist[i] - x))
	return ulist[ci]

def get_grand_pot(x_eval,T,npxlist,npZlist,expect_xlist,ulist):

	# x : pure input <x>
	# T : pure input
	
	# Zclist : Z canonical
	# xlist  : known x values
	# exlist / ulist for calculating chemical potential u(<x>)
	
	x_eval = np.float128(x_eval)
	T	   = np.float128(T)
	#npexpect_xlist = np.array(expect_xlist,dtype=np.float128)
	#npulist = np.array(ulist,dtype=np.float128)

	global _kb
	
	gp = np.float128(0.)
	
	for x,Z in zip(npxlist,npZlist):
		gp += np.exp(x*get_u_by_x(x_eval,expect_xlist,ulist)/_kb/T) * Z
	
	gp = -_kb*T*np.log(gp)
	
	return x_eval, gp, get_u_by_x(x_eval,expect_xlist,ulist)

#
# GCE ---- function end ---- -------------------------------------------------------------------
#

# USER DEF

freq_path = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/freq_pkl'					# frequency files path
rdf_path = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/rdf_pkl'
std_path = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/rdf_pkl'

# custom functions

# load any pkl file
def load_pkl(pklfile):
	return pd.read_pickle(pklfile)


# ---------------- output

print(f' ! ------------------------------------------------------------------------')
print(f' ! canonical analysis RDF')
print(f' * freq_path pkl form            : {freq_path}')
print(f' * rdf_path  pkl form            : {rdf_path}')
print(f' * std_path gulp_std_output(csv) : {std_path}')
print(f' ! Extrating info ...',flush=True)

freq_pkl_list = [ f'freq{i}.pkl' for i in range(25) ]		# DV - dummy variables
rdf_pkl_list = [ f'rdf{i}.pkl' for i in range(25) ]			# DV
std_csv_list = [ f'nconp{i}.csv' for i in range(25) ]		# DV

freq_pkl_paths = [os.path.join(freq_path, item) for item in freq_pkl_list]
rdf_pkl_paths = [os.path.join(rdf_path, item) for item in rdf_pkl_list]
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
for file in rdf_pkl_paths:
	fchecklist.append(os.path.exists(file))
if False not in fchecklist:
	print(f' * rdf_pkl	file check done')
else:
	print(f' * rdf_pkl file extracting failed')
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
rdf_dflist = []

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
	print(' ! size %.3d - [G,Z] :',end='')
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
ulist = [ float(i) * _du for i in range(-_bin,_rbin+1) ]
#
current_time = time.time()
print(f' ! ------------------------------------------------------------------------')
print(f' ! chemical pontential configuration')
print(f' ! bin range : {-_bin} ~ {_rbin}')
print(f' ! u window  : {-_bin*_du} ~ { _rbin*_du}')
print(f' ! delta u   : {_du}')
print(f' ! ------------------------------------------------------------------------')
print(f' * obtaining particle distribution fuction & expected <x>')
print(f' ! starts  at : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time)))

expect_xlist = []
for i,u in enumerate(ulist):
	print(f' ! working on : {i+1}/{len(ulist)}', end='\r')
	npwxlist = get_wx(npZlist,npxlist,u,_T)
	expect_x = get_expect_x(npxlist,npwxlist)
	expect_xlist.append(expect_x)

# writing u, x
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
print(f' ! delta x   : {_dx}')
print(f' ! ------------------------------------------------------------------------')
print(f' * obtaining inverted u(<x>,T)') 
print(f' ! starts  at : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time)))

# test accuracy
x_samplelist = [ 0.1*float(i+1) for i in range(10) ]
print(f' * inversion check -> compare to values in x_u_T{_T}.out file')
for x in x_samplelist:
	u = get_u_by_x(x,expect_xlist,ulist)
	print(f' | x,u : %20.12e%20.12e' % (x,u))

new_time = time.time()
print(f' ! ends   at  : ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_time)))
print(f' ! elapsed t  : {new_time - current_time}')
print(f' ! ------------------------------------------------------------------------')

sys.exit()

#
# Perform RDF Grand Canonical analysis
#
#  use : u = get_u_by_x(x,expect_xlist,ulist) -> to get chemical potential for a Li concentration <x>
#        ^^             ^
#  chemical potential   <x> Li concentration
#
#  prepared data set:
#  expect_xlist
#  ulist
#


# rdf_pkl_paths

# loading twotheta value
rdf_df = load_pkl(rdf_pkl_paths[0])
rdf_r = rdf_df[0]['r']
pairlist = ['MnMn','LiLi','TcTc','MnLi','MnTc','LiTc']
del rdf_df

for size, std_df in enumerate(std_dflist):

	print(f' * processing {size} rdf ...')	

	rdf_df = load_pkl(rdf_pkl_paths[size])		# DATA loading 
	
	# DEFINE variable 'rdf_ce_ints<dict>'
	rdf_ce_ints = {}
	for pair in pairlist:
		rdf_ce_ints[pair] = [ 0. for i in range(len(rdf_r)) ]	 # prepare empty ints

	# for this size / samples

	Elist = std_df['energy'].values
	Egm = np.float128(Elist[0])		# global minimum

	taskidlist = std_df['taskid'].values

	for k, (E,taskid) in enumerate(zip(Elist,taskidlist)):

		print(f" ! working on : {k}/{len(taskidlist)}", end='\r')

		rdf_data = rdf_df[taskid]			# get rdf for sample 'taskid'

		E = np.float128(E) - Egm

		# extract individual intensity - LiLi, LiTc, TcTc ... total (6)

		for pair in pairlist:

			for i, ints in enumerate(rdf_data[pair]):

				rdf_ce_ints[pair][i] += np.float128(ints) * expkbt(E,_T)
	
	# div 'Zc' + Egm calibration
	for pair in pairlist:

		rdf_ce_ints_nptmp = np.array(rdf_ce_ints[pair])
		rdf_ce_ints_nptmp = rdf_ce_ints_nptmp * np.exp(-Egm/_kb/_T) / npZlist[size]
		rdf_ce_ints[pair] = rdf_ce_ints_nptmp.tolist()

	print(f' ! writing rdf output ...')

	with open(f'RDF_{_T}_{size}.rdf','w') as f:

		for i,r in enumerate(rdf_r):

			f.write('%20.12e' % (r))
			for pair in pairlist:
				f.write('%20.12e' % (rdf_ce_ints[pair][i]))
			f.write('\n')

	# ordering : 'r' + pairlist = ['MnMn','LiLi','TcTc','MnLi','MnTc','LiTc']

	del rdf_df
