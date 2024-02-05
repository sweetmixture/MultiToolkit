#!/bin/python

import os,sys
import pandas as pd
import numpy as np
import pickle

import time
#current_time = time.time()
#new_time = time.time()
#time_difference = new_time - current_time
#print("Current Time:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time)))
#print("Time Difference (seconds):", time_difference)
#print(f' ! loading at ',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct)))
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






# USER DEF

freq_path = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/freq_pkl'					# frequency files path
rdf_path = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/rdf_pkl'
std_path = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/rdf_pkl'

# custom functions

# load any pkl file
def load_pkl(pklfile):
	return pd.read_pickle(pklfile)


# ---------------- output

print(f' ! canonical analysis rdf ---------')
print(f' * freq_path pkl form			 : {freq_path}')
print(f' * rdf_path  pkl form			 : {rdf_path}')
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
print(f' * temperature (K)     = {_T}')
print(f' * including vibration = {_include_vib}')

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
	print(npGlist[s],npZlist[s])

print(f' ! ------------------------------------------------------------------------')
print(f' * calculation of canonical G / Z done ...')
print(f' ! ------------------------------------------------------------------------')

#
# Perform XRD Canonical analysis
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
		rdf_ce_ints[pair] = [ 0. for i in range(len(rdf_r)) ]    # prepare empty ints

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
