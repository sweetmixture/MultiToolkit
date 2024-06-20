#!/bin/python

'''
	Author	:	wkjee
	Title	:	OutputParser

	Layout

	/root
		/Base
			Atoms.py	: Atom, Shell
			Clusters.py : Cluster
			Cells.py	: Cell
	/Extractor
		GULP.py		: GULP_Patterns, ExtractFHIaims
	  * FHIaims.py	: FHIaims_Patterns, ExtractFHIaims

		* 29.12.2023
		/FHIaims	: ...
			mos.py
'''

'''
	Description

	[a] require argument for spin-polarisation calculation: "-spin"

		e.g., python this_python_script.py -spin

	[b] for target analysis must specify which are the number for "HOMO" and "LUMO"

		go to line number --> 320/321 for up/down

	[c] for selecting number of states want to extract set min/max values (i.e., selecting +- how many HOMO(-?) and LUMO(+?)

		go to line number --> 411/412
'''

import os,sys,json
import numpy as np
import pandas as pd

#
# internal use function
#

# vector normalisation : vector<list:float>[3]
def normalize_vector(vector):

	vector = np.array(vector)

	vector_square = vector ** 2	# [a,b,c] -> [a*a, b*b, c*c]
	vector_ss	  = np.sum(vector_square) # a*a + b*b + c*c

	Return = vector_square / vector_ss # [a*a, b*b, c*c] / (a*a + b*b + c*c)

	return Return

# mode default -> spin 'none'
# mode 1 -> spin 'collinear'

_lspin = None
#
# required argument (sys) '-spin'
# if '-spin' used -> using spin collinear mode
#
try:
	for item in sys.argv:
		if item == '-spin':
			_lspin = True
		else:
			_lspin = False
except:
	pass
#
# root
#
_root = '/work/e05/e05/wkjee/Gold/nosoc_cube_estate/pbe0'

if _lspin == True:

	__hartree_to_ev = 27.211384500
	#
	# mos file check
	#

	_file_alpha = os.path.join(_root,'alpha.aims')
	_file_beta	= os.path.join(_root,'beta.aims')
	_file_geometry = os.path.join(_root,'geometry.in')

	if not os.path.exists(_file_alpha):
		print(f' @Error -> cannot find alpha channel mos file in the given path : {_file_alpha}',file=sys.stderr)
		sys.exit(1)
	else:
		print(f' ! alpha channel mos found at {_file_alpha}')
	if not os.path.exists(_file_beta):
		print(f' @Error -> cannot find beta channel mos file in the given path : {_file_beta}',file=sys.stderr)
		sys.exit(2)
	else:
		print(f' ! beta  channel mos found at {_file_beta}')

	#
	# basis function check
	#

	_file_basis = os.path.join(_root,'basis-indices.out')
	
	if not os.path.exists(_file_basis):
		print(f' @Error -> cannot find basis function info in the given path : {_file_basis}',file=sys.stderr)
		sys.exit(1)
	else:
		print(f' ! bassis function file found at {_file_basis}')

	# ------------------------------------------------------ input file checker

	#
	# loading 'basis-indices.out' file : basis functions
	#

	'''
		convention : number / type / atom_number / n l m
	'''
	basis_set = [] # SAVE_ON_MEM
	#
	# basis_set structure
	#
	# <list:dict>
	# basis_set = [ 
	#				{'number'	   : <int>, # basis number
	#				 'type'		   : <str>, # orbital type: atomic, ionic, hydro ..
	#				 'atom_number' : <int>, # this matches with 'species' in geometry.in file
	#				 'n'		   : <int>,
	#				 'l'		   : <int>,
	#				 'm'		   : <int>,
	#				 'species'	   : <str>	# atom name or species name
	#				},
	#			  ... # repeat same dictionlary 
	#			  ]
	try:
		# 1st pass
		with open(_file_basis,'r') as f:
			for line in f:
				ls = line.split()
				
				try:
					int(ls[0])	# forced check if integer ... # FHIaims-basis set info starts with integer
					basis = {'number': int(ls[0]), 'type': ls[1], 'atom_number': int(ls[2]), 'n': int(ls[3]), 'l': int(ls[4]), 'm': int(ls[5])}
					basis_set.append(basis)
				except:
					pass

		# 2nd pass
		# get atom 'species'
		with open(_file_geometry,'r') as f:
			atom_index = 1
			for line in f:
				if 'atom' in line:
					species = line.split()[-1]
					# looping 'basis_set' list and add 'species'
					for basis in basis_set:
						if basis['atom_number'] == atom_index:
							basis['species'] = species
					atom_index = atom_index + 1			
	except:
		print(f' @Error cannot read basis-indices.out at {_file_basis}',file=sys.stderr)
		sys.exit(1)

	# ========================================
	__dev_bcheck = False
	# dev check basis
	if __dev_bcheck == True:
		print(f'basis set 40')
		basis = basis_set[39]
		print(f"basis number	 : {basis['number']}")
		print(f"basis type		 : {basis['type']}")
		print(f"basis atom_number: {basis['atom_number']}")
		print(f"basis n / l / m  : {basis['n']} / {basis['l']} / {basis['m']}")
	# ========================================
	#
	# loading 'alpha.aims' / 'beta.aims' files
	#

	ks_vectors_up = []	 # SAVE_ON_MEM
	ks_vectors_down = [] # SAVE_ON_MEM	
	#
	# * data structure
	#
	# ks_vector_up/down = [
	#						{'channel'		 : <str>,		# 'up'/'down'
	#						 'state'		 : <int>,
	#						 'eigenvalue'	 : <float>,		# Ha unit
	#						 'eigenvalue_ev' : <float>,		# eV unit
	#						 'eigenvector'	 : <list:float> # evec_list
	#						},
	#					  ...
	#					  ]
	try:
		# read spin channel 'alpha'
		print(f' Reading-in alpha ...')
		with open(_file_alpha,'r') as fa:

			for line in fa:

				# capture 'eigenvalue' pattern in line
				if 'eigenvalue' in line:
					ls = line.split()

					state = int(ls[0])	# state number
					nsaos = int(ls[-1]) # number of eigenvector elements
					eigenv = float(ls[2][11:].replace('D','E'))
					channel = 'up'

					next_line_count = nsaos//4	# number of lines to read
					last_line_residue = nsaos%4 # number of elements in the last line

					# return
					evec_list = []

					# read eigenvectors
					for i in range(next_line_count):
						nline = next(fa)

						evec_list.append(float(nline[0:20].replace('D','E')))
						evec_list.append(float(nline[20:40].replace('D','E')))
						evec_list.append(float(nline[40:60].replace('D','E')))
						evec_list.append(float(nline[60:80].replace('D','E')))
	
					if last_line_residue > 0:
						nline = next(fa)

						for i in range(last_line_residue):
							evec_list.append(float(nline[:20].replace('D','E')))
							nline = nline[20:] # cut first 20 characters
					
					ks_vector = {'channel':channel,'state':state,'eigenvalue':eigenv, 'eigenvalue_ev': eigenv * __hartree_to_ev, 'eigenvector':evec_list}
					ks_vectors_up.append(ks_vector)

			print(f' ! reading in channel alpha done')

	except:
		print(f' @Error cannot read mos files at: {_file_alpha}',file=sys.stderr)
		sys.exit(1)

	try:
		# read spin channel 'beta'
		print(f' Reading-in beta ...')
		with open(_file_beta,'r') as fb:

			for line in fb:

				# line capture 'eigenvalue'
				if 'eigenvalue' in line:
					ls = line.split()

					state = int(ls[0])
					nsaos = int(ls[-1])
					eigenv = float(ls[2][11:].replace('D','E'))
					channel = 'down'

					next_line_count = nsaos//4
					last_line_residue = nsaos%4

					evec_list = []

					# read eigenvectors
					for i in range(next_line_count):
						nline = next(fb)

						evec_list.append(float(nline[0:20].replace('D','E')))
						evec_list.append(float(nline[20:40].replace('D','E')))
						evec_list.append(float(nline[40:60].replace('D','E')))
						evec_list.append(float(nline[60:80].replace('D','E')))

					if last_line_residue > 0:
						nline = next(fb)

						for i in range(last_line_residue):
							evec_list.append(float(nline[:20].replace('D','E')))
							nline = nline[20:]

					ks_vector = {'channel':channel,'state':state,'eigenvalue':eigenv, 'eigenvalue_ev': eigenv * __hartree_to_ev, 'eigenvector':evec_list}
					ks_vectors_down.append(ks_vector)

			print(f' ! reading in channel beta done')

	except:
		print(f' @Error cannot read mos files at: {_file_beta}',file=sys.stderr)
		sys.exit(1)

	print(f'-------------------------------------')
	print(f' Reading in KS vectors finished')
	print(f'-------------------------------------')


	# data set check
	#for i in range(10):
	#	print(basis_set[i])
	#
	#for i in range(10):
	#	print(ks_vectors_up[i])


	'''
		source : /work/e05/e05/wkjee/Gold/run2/FHIaims.out
		spin up   (HOMO) : 1555
		spin down (HOMO) : 1554

		@ 02.01.2024
		data structure

			basis_set<list>(<dict>) -> basis : {'number': basis_number , 'type': fhiaims_basis_type, 'atom_number': atom_number_in_geometry, 'n': , 'l': , 'm': , 'species': element_name }
			ks_vectors_up/down<list>(dict) -> {'channel': 'up/down', 'state': state_number , 'eigenvalue': eigenv_Ha , 'eigenvalue_ev': eigenv_eV,'eigenvector': evec_list }
	'''
	#
	# USER CONTROL: test - treating HOMO alpha
	#
	# * for this example case
	# spin-up HOMO	 : 1555
	# spin-down HOMO : 1554
	up = 1555 - 1
	down = 1554 - 1

	HOMOup = ks_vectors_up[up]
	LUMOup = ks_vectors_up[up+1] 

	eigenvalues = [ HOMOup['eigenvalue_ev'], LUMOup['eigenvalue_ev'] ]

	#print(len(basis_set),len(HOMOup))
	# normalization

	HOMOup_eveclist = np.array(HOMOup['eigenvector'])
	LUMOup_eveclist = np.array(LUMOup['eigenvector'])

	HOMOup_evec_square = HOMOup_eveclist ** 2
	LUMOup_evec_square = LUMOup_eveclist ** 2

	HOMOup_evec_ss = np.sum(HOMOup_evec_square)
	LUMOup_evec_ss = np.sum(LUMOup_evec_square)

	# numpy array
	HOMOup['eigenvector'] = HOMOup_evec_square / HOMOup_evec_ss
	LUMOup['eigenvector'] = LUMOup_evec_square / LUMOup_evec_ss

	# normalization ----- done

	#
	# stacking Au / S / Others
	#

	Au = 0.
	S  = 0.
	O  = 0.

	for basisf,velem in zip(basis_set,HOMOup['eigenvector']):

		if basisf['species'] == 'Au':
			Au = Au + velem
		elif basisf['species'] == 'S':
			S = S + velem
		else:
			O = O + velem

	print('upHOMO',Au,S,O)

	Au = 0.
	S  = 0.
	O  = 0.

	for basisf,velem in zip(basis_set,LUMOup['eigenvector']):

		if basisf['species'] == 'Au':
			Au = Au + velem
		elif basisf['species'] == 'S':
			S = S + velem
		else:
			O = O + velem

	print('upLUMO',Au,S,O)
	print(eigenvalues)

	
	# Plot Test
	'''
		d = {
		'HOMO': [0.4910104395437078, 0.42156993757248906, 0.08741962288380328],
		'LUMO': [0.6097841544993644, 0.30795764376772655, 0.08225820173290874],
		}
		
		[-6.592289964648314, -4.837035439647899]
	'''

	print('---------- Test Done ----------')

	# ===============================================================================================
	# EXTRACTING ...
	# ===============================================================================================
	# using 'basis_set' / 'ks_vector_up/down'
	# Extracting +8 / -8
	# 

	spin_up_states = []
	spin_down_states = []

	up_state_evals = []
	down_state_evals = []
	up_state_index = []
	down_state_index = []
	# up   = 1555 - 1 = 1554 
	# down = 1554 - 1 = 1553
	
	_min_limit = +8 # USER_CONTROL : scanning ks state bottom limit
	_max_limit = +8 # USER_CONTROL : scanning ks state top limit
	# this setting -8,-7,...,0,1,2,...,8

	#
	# GET KS_VECTORS
	#
	for i in range(-_min_limit,_max_limit+1):
		spin_up_states.append(ks_vectors_up[up-i])		 # up	: HOMO index
		spin_down_states.append(ks_vectors_down[down-i]) # down : HOMO index
	# up   state: 1554-8, 1554-7, ... , 1554+8 : [1546,1562]
	# down state: 1553-8, 1554-7, ... , 1553+8 : [1545,1561]

	for up_state,down_state in zip(spin_up_states,spin_down_states):
		up_state_evals.append(up_state['eigenvalue_ev'])
		up_state_index.append(up_state['state'])
		down_state_evals.append(down_state['eigenvalue_ev'])
		down_state_index.append(down_state['state'])

	#
	# PRINT EIGENVALUE OUTPUT
	#
	print(f'')
	print(f' ! ===========================')
	print(f' ! KS EIGENVALUE INFO')
	print(f' ! ===========================')
	print(f' * spin up state eigenvalues (eV)')
	for k,ev in zip(up_state_index,up_state_evals):
		print(f' {k:5d}{ev:20.12f}')
	print(f' * spin down state eigenvalues (eV)')
	for k,ev in zip(down_state_index,down_state_evals):
		print(f' {k:5d}{ev:20.12f}')
	# saving order top(LOMO) -> bottom(HOMO)
	#
	
	# saving occupancy, i.e., normalised ks vetors
	# using 
	# spin_up_states / spin_down_states
	up_state_occ = []
	down_state_occ = []

	for up_state,down_state in zip(spin_up_states,spin_down_states):

		# normalize : [a*a, b*b, c*c] / (a*a + b*b + c*c)
		up_state['eigenvector'] = normalize_vector(up_state['eigenvector'])
		down_state['eigenvector'] = normalize_vector(down_state['eigenvector'])

		# processing up-state ---
		# extract desired occupancies
		Au_sp = 0. # n6 l0 s / n6 l1 p
		Au_d = 0.  # n5 l2 d
		S_p = 0.   # n3 l1
		O  = 0.    # others

		for basisf,velem in zip(basis_set,up_state['eigenvector']):

			if basisf['species'] == 'Au':

				if basisf['n'] == 6 and basisf['l'] == 0:
					Au_sp = Au_sp + velem
				elif basisf['n'] == 6 and basisf['l'] == 1:
					Au_sp = Au_sp + velem
				elif basisf['n'] == 5 and basisf['l'] == 2:
					Au_d = Au_d + velem
				else:
					O = O + velem

			elif basisf['species'] == 'S':

				if basisf['n'] == 3 and basisf['l'] == 1:
					S_p = S_p + velem
				else:
					O = O + velem
			else:
				O = O + velem

		up_state_occ.append([Au_sp,Au_d,S_p,O])

		# processing down-state ---
		Au_sp = 0.
		Au_d = 0.
		S_p = 0.
		O  = 0.

		for basisf,velem in zip(basis_set,down_state['eigenvector']):

			if basisf['species'] == 'Au':

				if basisf['n'] == 6 and basisf['l'] == 0:
					Au_sp = Au_sp + velem
				elif basisf['n'] == 6 and basisf['l'] == 1:
					Au_sp = Au_sp + velem
				elif basisf['n'] == 5 and basisf['l'] == 2:
					Au_d = Au_d + velem
				else:
					O = O + velem

			elif basisf['species'] == 'S':

				if basisf['n'] == 3 and basisf['l'] == 1:
					S_p = S_p + velem
				else:
					O = O + velem

			else:
				O = O + velem

		down_state_occ.append([Au_sp,Au_d,S_p,O])


	# up_state_evals = []
	# down_state_evals = []
	# up_state_index = []
	# down_state_index = []
	# up_state_occ
	# down_staet_occ

	#
	# create json
	#
	up_spin_json = {}
	down_spin_json = {}

	# processing up state
	for k,ev,occ in zip(up_state_index,up_state_evals,up_state_occ):
		#up_spin_json[k]['eval'] = ev
		#up_spin_json[k]['occ'] = occ
		up_spin_json[k] = {}
		up_spin_json[k]['eval'] = ev
		up_spin_json[k]['occ'] = occ
	with open('selected_up.json', 'w') as log_file:
		json.dump(up_spin_json, log_file, indent=4)
	# processing down state
	for k,ev,occ in zip(down_state_index,down_state_evals,down_state_occ):
		#down_spin_json[k]['eval'] = ev
		#down_spin_json[k]['occ'] = occ
		down_spin_json[k] = {}
		down_spin_json[k]['eval'] = ev
		down_spin_json[k]['occ'] = occ
	with open('selected_down.json', 'w') as log_file:
		json.dump(down_spin_json, log_file, indent=4)


	# --- printing
	print('up state eval ---')
	for up_state_eval in up_state_evals:
		print(f'{up_state_eval}, ',end='')
	print('')
	for occ in up_state_occ:
		print(occ)

	print('down state eval ---')
	for down_state_eval in down_state_evals:
		print(f'{down_state_eval}, ',end='')
	print('')
	for occ in down_state_occ:
		print(occ)




	# ks_vectors_up/down<list>(dict) -> {'channel': 'up/down', 'state': state_number , 'eigenvalue': eigenv_Ha , 'eigenvalue_ev': eigenv_eV,'eigenvector': evec_list }

	


