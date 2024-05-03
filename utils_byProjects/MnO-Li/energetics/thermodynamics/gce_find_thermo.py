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
def get_gz(csvdf,T,vib=False,pkldf=None,ref_freqlist=None):

	global _kb
	global _wavenumber_to_ev
	#u = np.float128(0.)	# _corr

	Elist = csvdf['energy'].values
	Egm = np.float128(Elist[0])		# global minimum

	T = np.float128(T)
	Z = np.float128(0.)
	G = np.float128(0.)

	_norm_n = np.float128(24.)		# HARD_CODED -> to make the f.u.
	# check
	#print(f'dataset Elist length: {len(Elist)}')

	if vib == False:

		for E in Elist:
			E = np.float128(E) - Egm
			Z += expkbt(E,T)
		
		#Z = np.exp(-Egm/_kb/T) * Z	
		Z = np.exp(-Egm/_kb/T) * Z / np.float128(len(Elist))
		G = - _kb * T * np.log(Z)
		#print(Egm,-Egm/_kb/T,np.exp(-Egm/_kb/T),Z,G)
	#
	# include vibrational contributions
	# WKJee 03.24 added : full vibrational modes using quantum number
	#
	elif vib == True:
		#
		# looping (states) structures / distinguished by 'taskid'
		#
		for E,taskid in zip(Elist,csvdf['taskid'].values):

			E = np.float128(E) - Egm
			ZE = expkbt(E,T)

			#
			# get freq info for this struct
			#
			freqlist = np.array(pkldf[taskid],dtype=np.float128)
			# add ZPE contribution - at the gamma point
			freq0_power = np.float128(0.)

			# ! NEW : for quantum 'n' -> 0,1,2,...,inf
			freq_infsum = np.float128(1.)

			#
			# looping all modes
			#
			for freq in freqlist:
				# zpe 
				freq0_power += (0.5 * freq * _wavenumber_to_ev)	# this term is exactly same with ZPE
				# all vib
				freq_infsum *= (1./(1. - np.exp(-freq*_wavenumber_to_ev/_norm_n/_kb/T)))  # 24 HARD_CODED for normalisation per f.u.

			#Zvib0 = np.exp(-freq0_power/_kb/T)
			Zvib0 = np.exp(-freq0_power/_norm_n/_kb/T)		# 24 HARD_CODED for normalisation per f.u.
			# for quantum 'n': add all vib contribution
			Zinfsum = freq_infsum

			# sum up
			Z += (ZE * Zvib0 * Zinfsum)
			#! Z += (ZE * Zvib0)

		# pull back Egm
		Z = np.exp(-Egm/_kb/T) * Z / np.float128(len(Elist))		# division 10000 -> HARD_CODED need to be corrected
		G = - _kb * T * np.log(Z)

		# ------------
		# NEW_ADDITION reference freq list treatment
		# ------------
		ref_freq0_power = np.float128(0.)
		ref_freq_infsum = np.float128(1.)
		for freq in ref_freqlist:			# this ref_freqlist : after dropping out rot/trans + no negative
			# zpe reference
			ref_freq0_power += (0.5 * freq * _wavenumber_to_ev)
			# all vib reference
			ref_freq_infsum *= (1./(1. - np.exp(-freq*_wavenumber_to_ev/_norm_n/_kb/T)))

		rZvib0 = np.exp(-ref_freq0_power/_norm_n/_kb/T)
		rZinfsum = ref_freq_infsum

		# ------------
		# NEW_ADDITION : Li Correction? : exp(-E_ZP/kbT) * ProdSum(j) 1/(1 - exp(-hcvj/kbT))
		# ------------
		# this modification must be done on Ecorr term !! or as : (x * Evib_corr)

		Z = Z / rZvib0 / rZinfsum
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





_Tc = _T
# VERY IMPORTANT USER PARAMETER : SETTING delta T for central difference method to calculate 'S'
#_dT = 0.025
_dT = 0.5
_Tf = _T + _dT
_Tb = _T - _dT
_Tfb = [_Tf,_Tb]

for _T in _Tfb:

	_T = np.float128(_T)

	#
	# G,Z =  def get_gz(csvdf,T,vib=False):
	#
	npGlist = np.zeros(len(std_dflist),dtype=np.float128)
	npZlist = np.zeros(len(std_dflist),dtype=np.float128)
	
	for s, (std_df,freq_df) in enumerate(zip(std_dflist,freq_dflist)):
	
		#print(f' * processing partition function Z : size {s}')
		#Gc,Zc = get_gz(std_df,_T,vib=_include_vib,pkldf=freq_df)		# MUST INCLUDE VIB FOR X = 0 Otherwise -> ERRRRRORRRRR!!!
		Gc,Zc = get_gz(std_df,_T,vib=_include_vib,pkldf=freq_df,ref_freqlist=np.array(freq_dflist[0][0],dtype=np.float128))

		npGlist[s] = Gc
		npZlist[s] = Zc
	
		#print(' ! size %.3d - [G,Z] : %20.12e%20.12e' % (s,npGlist[s],npZlist[s]))		# inf error in low T e.g., 10K
		print(f' ! size {s} - [G,Z] :',end='')
		print(npGlist[s],'\t',npZlist[s])
	
	print(f' ! ------------------------------------------------------------------------')
	print(f' * calculation of canonical G / Z done ...')
	print(f' * temperature : {_T} K')
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
		with ProcessPoolExecutor(max_workers=16) as executor:								# 64 cpus may cause deadlock depending on the login-node status
		#with ProcessPoolExecutor() as executor:
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

# end after printing x, u, -u


# USER : MUST USE kJ
# use trapz integration
_unitJ = True
#
#	calculting dΔG(x,T)/dx calculator
#
def get_dgasx(_T):

	global _unitJ

	_file = f'x_u_T{_T}.out'

	with open(_file,'r') as f:

		data = np.loadtxt(f,skiprows=1,dtype=np.float128)

		xlist = data[:,0]	# x 
		vlist = data[:,1]	# chemical_potential (u)

	if _unitJ == True:
		for k,v in enumerate(vlist):
			vlist[k] = v * 96485.3321

	return xlist, vlist

#
#   calculating ΔG(x,T)
#
def get_gasx(_T):

	global _unitJ

	_file = f'x_u_T{_T}.out'

	with open(_file,'r') as f:

		data = np.loadtxt(f,skiprows=1,dtype=np.float128)

		xlist  = data[:,0]	# col 1
		ulist  = data[:,1]	# col 2
		#_ulist = data[:,2]  # col 3


	of = open(f'x_g_T{_T}.out','w')
	if _unitJ == True:
		of.write('%20s  %20s\n' % ('x','G(J/mol)'))
	else:
		of.write('%20s  %20s\n' % ('x','G(eV)'))
	#
	# integate for x [0:x]
	#

	retilist = []
	retxlist = []

	for k,x in enumerate(xlist):

		#print(x,xlist[k])

		if k+1 == len(xlist):
			break

		int_xrange = xlist[:k+2]
		int_yrange = ulist[:k+2]

		if _unitJ == True:
			I = np.trapz(int_yrange,int_xrange) * 96485.3321 # V
		else:
			I = np.trapz(int_yrange,int_xrange)
			
		of.write('%20.12e  %20.12e\n' % (int_xrange[-1],I))

		retilist.append(np.float128(I))
		retxlist.append(np.float128(int_xrange[-1]))

	of.close()

	return retxlist, retilist

# --------------------------------------------------------
xflist,gflist = get_gasx(_Tf)
xblist,gblist = get_gasx(_Tb)

xflist,vflist = get_dgasx(_Tf)
xblist,vblist = get_dgasx(_Tb)

print(f' * front/backward free energy ready ...')

#_dT = 0.025
#_Tf = _T + _dT
#_Tb = _T - _dT
#_Tfb = [_Tf,_Tb]

def get_near_indices(datalist,x):

	ksta = None
	kend = None

	for k,data in enumerate(datalist):
		if x < data:
			kend = k
			ksta = k - 1
			break

	return ksta, kend

def get_gval(p1,p2,x):

	x1, y1 = p1
	x2, y2 = p2

	a = (y2 - y1) / (x2 - x1)
	b = y1 - a * x1
	
	return a * x + b

# USER
_dsx = 0.01
_dsx = 0.0025
#
sxlist = [ float(i+1)*_dsx for i in range(int(1./_dsx)-1) ]		# warning -> must exclude boundary x = 0 and 1

of = open(f'HST{_Tc}_d{_dT}.out','w')
if _unitJ == True:
	of.write('%20s  %20s  %20s %20s\n' % ('x','ΔG(kJ/mol)','ΔH(kJ/mol)','ΔS(J/mol/K)'))
else:	
	of.write('%20s  %20s  %20s %20s\n' % ('x','ΔG(eV)','ΔH(eV)','ΔS(eV/K)'))


print(f' ! ------------------------------------------------------------------------')
print(f' * printing enthalpy, entropy')
print(f' ! T       = {_Tc} K')
print(f' ! delta T = {_dT} K used for numerical calculation')
print(f' ! delta x = {_dsx} for {int(1./_dsx)} data points')
print(f' ! ------------------------------------------------------------------------')

for x in sxlist:

	# front free energy
	fksta, fkend = get_near_indices(xflist,x)
	fx1 = xflist[fksta]
	fx2 = xflist[fkend]
	fg1 = gflist[fksta]
	fg2 = gflist[fkend]
	# get fg for 'x'
	fg = get_gval((fx1,fg1),(fx2,fg2),x)

	# backward free energy
	bksta, bkend = get_near_indices(xblist,x)
	bx1 = xblist[bksta]
	bx2 = xblist[bkend]
	bg1 = gblist[bksta]
	bg2 = gblist[bkend]
	# get bg for 'x'
	bg = get_gval((bx1,bg1),(bx2,bg2),x)

	# caclulate entropy 's' with central difference method

	#if _unitJ == True:
	#	s = - (fg - bg) / 2. / _dT * 96491.5666
	#else:
	#	s = - (fg - bg) / 2. / _dT

	# units are in J
	s = - (fg - bg) / 2. / _dT
	g = (fg + bg) / 2.	
	h = g + s * _Tc

	# J -> kJ for G and H
	of.write('%20.12e  %20.12e	%20.12e  %20.12e\n' % (x,g/1000.,h/1000.,s))

of.close()

#
# WKJEE. 21/03/2024
# DO NOT TRUST RESULTS BY BELOW
#
of = open(f'dHST{_Tc}_d{_dT}.out','w')
if _unitJ == True:
	of.write('%20s  %20s  %20s %20s\n' % ('x','dΔG/dx(kJ/mol)','dΔH/dx(kJ/mol)','dΔS/dx(J/mol/K)'))
else:	
	of.write('%20s  %20s  %20s %20s\n' % ('x','dΔG/dx(eV)','dΔH/dx(eV)','dΔS/dx(eV/K)'))

for x in sxlist:

	# front V
	fksta, fkend = get_near_indices(xflist,x)
	fx1 = xflist[fksta]
	fx2 = xflist[fkend]
	fv1 = vflist[fksta]
	fv2 = vflist[fkend]
	# get fv for 'x'
	fv = get_gval((fx1,fv1),(fx2,fv2),x)

	# backward V
	bksta, bkend = get_near_indices(xblist,x)
	bx1 = xblist[bksta]
	bx2 = xblist[bkend]
	bv1 = vblist[bksta]
	bv2 = vblist[bkend]
	# get bv for 'x'
	bv = get_gval((bx1,bv1),(bx2,bv2),x)

	# units are in J
	ds = - (fv - bv) / 2. / _dT		# 
	dg = (fv + bv) / 2.	
	dh = dg + ds * _Tc

	# J -> kJ for G and H
	of.write('%20.12e  %20.12e	%20.12e  %20.12e\n' % (x,dg/1000.,dh/1000.,ds))
