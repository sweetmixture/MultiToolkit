#
#	UV-VIS FHIaims analyser
#
#	07.2024 WKJEE
#
import numpy as np
import sys,os
import json
from Transition_ReIm import get_trans_int_full # (icube_filelist,fcube_filelist,verbose=False):

_skiplines = 7
_fhiaims_soc_eval_file = 'SOC_eigenvalues.dat'

#
#	Read EigenValue data
#
soc_eval = {}
with open(_fhiaims_soc_eval_file,'r') as f:
	
	# skip texts
	for _ in range(_skiplines):
		next(f)

	# line consists of 'State    Occupation    Unperturbed Eigenvalue [eV]    Eigenvalue [eV]    Level Spacing [eV]  '

	print(f" * ---------------------------------------------")
	print(f" * Loading ... eigenvalue data")

	for line in f:

		contents = line.strip().split()
		
		if len(contents) < 1:
			break

		sample_data = { 
						'occ'     : float(contents[1]),
						'eval'    : float(contents[2]),
						'soc_eval': float(contents[3]),
					  }
		
		soc_eval[int(contents[0])] = sample_data

#
#	Get Key states
#
def get_homo_state(soc_eval):

	homo_state = None

	for state in soc_eval:

		if soc_eval[state]['occ'] != soc_eval[state+1]['occ']:	# when occ changes from '1' --> '0'

			print(f" * ---------------------------------------------")
			print(f" * HOMO state: {state}")
			print(f" * evalue    : {soc_eval[state]['eval']}")
			print(f" * soc-evalue: {soc_eval[state]['soc_eval']}")
			print(f" * ---------------------------------------------")
			homo_state = state
			break

	return state

# -------------------------------------------------------------------------------------------------
# USER

#_scan_range = 8		#  3101 - 3118
_scan_range = 9		#  3100 - 3119
#_scan_range = 15	#  3094 - 3125
#_bottom = 8	# obtain HOMO-7 ... HOMO+0
#_top    = 8 # obtain LUMO+0 ... LUMO+7
# HOMO - 3109

homo_state = get_homo_state(soc_eval)
lumo_state = homo_state + 1
#
#	extract states
#
homo_states = []
lumo_states = []

for i in range(_scan_range+1):

	homo_states.append(homo_state-i)
	lumo_states.append(lumo_state+i)

homo_states = sorted(homo_states,reverse=False)
print(f" * selected homo states: {homo_states}")
print(f" * selected lumo states: {lumo_states}")
print(f" * ---------------------------------------------")

print(f" * list of selected states : evals / soc-evals (eV)")
print(f" * ---------------------------------------------")
#
# GET HOMO SOC-STATE EVALS
for key in soc_eval.keys():
	if key in homo_states:
		print(f" [h] state/eval : {key:6d}{soc_eval[key]['eval']:20.12f}{soc_eval[key]['soc_eval']:20.12f}")
#
# GET LUMO SOC-STATE EVALS
for key in soc_eval.keys():
	if key in lumo_states:
		print(f" [l] state/eval : {key:6d}{soc_eval[key]['eval']:20.12f}{soc_eval[key]['soc_eval']:20.12f}")
print(f" * ---------------------------------------------")

# -------------------------------------------------------------------------------------------------

#
#	Get Atom List
#
_fhiaims_geometry_file = 'geometry.in'

atomlist = {}
with open(_fhiaims_geometry_file,'r') as f:
	atom_count = 1
	for line in f:
		if 'atom' in line:
			ls = line.strip().split()
			atomlist[atom_count] = ls[4]
			atom_count += 1
# DEV_CHECK
#for key in atomlist.keys():
#	print(f'{key:4d}   {atomlist[key]:10s}')
#   atomlist[atom_no<int>] -> return atom string

#
#	Get EigenStates
#
_fhiaims_soc_evec_file = 'SOC_eigenvectors_k_point_1'


homo_evecs = {}
lumo_evecs = {}

#
#	Get Maximum States Count
#
_state_count_max = len(homo_states) + len(lumo_states)
_state_count = 0

with open(_fhiaims_soc_evec_file,'r') as f:

	print(f" * Loading ... eigenvector data")
	print(f" * ---------------------------------------------")


	while True:

		line = f.readline().strip()

		contents = line.split()

		if 'Eigenstate' in line:

			#
			#   Get HOMO states
			#	catch pattern 'Eigenstate'
			if int(contents[1]) in homo_states:
				_state_count += 1
				_state = int(contents[1])

				# skip text line : containing 'Basis#  Atom# type      n l   m s     coefficient'
				f.readline()

				homo_evecs[_state] = []

				while True:
					evec = {}
																# basis contents: 'Basis#  Atom# type      n l   m s     coefficient'
					basis_info = f.readline().strip().split()	# 1     1 atomic    1 s   0 up    -0.000006790707928 +  -0.000019140009185 * i
					#print(basis_info,len(basis_info))
					# If 'basis_info' reaches to the last line of an evec
					if len(basis_info) < 1:
						break

					evec['basis_no'] = int(basis_info[0])
					evec['atom_no']  = int(basis_info[1])
					evec['type']     = basis_info[2]        # atomic/hydro/...
					evec['n']        = int(basis_info[3])   # 1/2/3/..
					evec['l']        = basis_info[4]        # s/p/d/f...
					evec['m']        = int(basis_info[5])   # -1/0/1
					evec['spin']     = basis_info[6]        # up/dn
					evec['c_real']   = float(basis_info[7])
					evec['c_imag']   = float(basis_info[9])

					homo_evecs[_state].append(evec)	# save evec line for '_state'

			#
			# Get LUMO states
			# catch pattern 'Eigenstate'
			if int(contents[1]) in lumo_states:
				_state_count += 1
				_state = int(contents[1])

				# skip text line : containing 'Basis#  Atom# type      n l   m s     coefficient'
				f.readline()

				lumo_evecs[_state] = []
				while True:
					evec = {}
																# basis contents: 'Basis#  Atom# type      n l   m s     coefficient'
					basis_info = f.readline().strip().split()	# 1     1 atomic    1 s   0 up    -0.000006790707928 +  -0.000019140009185 * i

					# If 'basis_info' reaches to the last line of an evec
					if len(basis_info) < 1:
						break

					evec['basis_no'] = int(basis_info[0])
					evec['atom_no']  = int(basis_info[1])
					evec['type']     = basis_info[2]        # atomic/hydro/...
					evec['n']        = int(basis_info[3])   # 1/2/3/..
					evec['l']        = basis_info[4]        # s/p/d/f...
					evec['m']        = int(basis_info[5])   # -1/0/1
					evec['spin']     = basis_info[6]        # up/dn
					evec['c_real']   = float(basis_info[7])
					evec['c_imag']   = float(basis_info[9])

					lumo_evecs[_state].append(evec)	# save evec line for '_state'
			
		if _state_count == _state_count_max:

			print(f' * soc-eigenvector scanning done')
			print(f" * ---------------------------------------------")
			break
# 
# 
# #
# #	[1] Check evec scanning
# #
# print(f' * homo evecs count : {len(homo_evecs)}')
# print(f' * lumo evecs count : {len(lumo_evecs)}')
# 
# #
# #	[1] Check evec scanning
# #	key check
# 
# for key in homo_evecs.keys():
# 	print(key)
# for key in lumo_evecs.keys():
# 	print(key)
# 
# # 	Specific state check
# _state = 3109
# 
# if _state in homo_evecs.keys():
# 	for item in homo_evecs[_state]:
# 		print(item)
# 
# 

# {'basis_no': 4765, 'atom_no': 259, 'type': 'hydro', 'n': 2, 'l': 'p', 'm': 0, 'spin': 'dn', 'c_real': 1.3360482519e-05, 'c_imag': 6.0067479669e-05}

#
# USE 'homo_states', 'lumo_states'
# USE 'soc_eval'
# USE 'atomlist'
#
# USE 'homo_evecs', 'lumo_evecs'
#

#
# DATA STRUCTURE DESCRIPTION
#

#
# 'homo_states' : list of states (integers)
# 'lumo_states' : list of states (integers)
#

#
# 'soc_eval' : { state<int> :
#					{ 'occ'     : 0 or 1,
#					  'eval'    : float (eV),
#					  'soc_eval': float (eV),
#					},
#					...
#				}
#

#
# 'atomlist' : { atom#<int> : species,
#				...
#				}
#

# ---------------------------------------------------------------------------------------
# Find Orbital Occupancies
# ---------------------------------------------------------------------------------------

#
# specific state check
#
_state = 3109

#
# BASIS SET LOADING CHECK
#
#if _state in homo_evecs.keys():
#	for basis in homo_evecs[_state]:
# POSSIBLE OUTPUT : {'basis_no': 1, 'atom_no': 1, 'type': 'atomic', 'n': 1, 'l': 's', 'm': 0, 'spin': 'up', 'c_real': -3.867159854e-06, 'c_imag': -2.1400239085e-05}
#		print(basis)

#
# UPDATE EIGENVECTOR - NORMALISATION
#
for state in homo_states:

	_state = state

	up_csqr = 0.
	dn_csqr = 0.
	csqr = 0.

	t_up_csqr = 0.
	t_dn_csqr = 0.
	t_csqr = 0.

	#
	# Iterate selected states 
	if _state in homo_evecs.keys():

		#
		# get normalise factor
		for basis in homo_evecs[_state]:	# iterate item (json or dict object)
			# 'up' state
			if basis['spin'] == 'up':
				cre = basis['c_real']
				cim = basis['c_imag']
				up_csqr += cre**2. + cim**2.
			# 'dn' state
			if basis['spin'] == 'dn':
				cre = basis['c_real']
				cim = basis['c_imag']
				dn_csqr += cre**2. + cim**2.
		
		# Get sum of squre of the coefficients 'csqr'
		# Get square root of 'csqr' --> 'nsqr' : for normalisation
		csqr = up_csqr + dn_csqr
		nsqr = np.sqrt(csqr)

		#
		# normalise
		#
		for basis in homo_evecs[_state]:
			#
			# UPDATE NORMALISED BASIS SET COEFFICIENT
			basis['c_real'] = basis['c_real'] / nsqr
			basis['c_imag'] = basis['c_imag'] / nsqr

#
# UPDATE EIGENVECTOR - NORMALISATION
#
for state in lumo_states:

	_state = state

	up_csqr = 0.
	dn_csqr = 0.
	csqr = 0.

	t_up_csqr = 0.
	t_dn_csqr = 0.
	t_csqr = 0.

	#
	# Iterate selected states 
	if _state in lumo_evecs.keys():

		#
		# get normalise factor
		for basis in lumo_evecs[_state]:	# iterate item (json or dict object)
			# 'up' state
			if basis['spin'] == 'up':
				cre = basis['c_real']
				cim = basis['c_imag']
				up_csqr += cre**2. + cim**2.
			# 'dn' state
			if basis['spin'] == 'dn':
				cre = basis['c_real']
				cim = basis['c_imag']
				dn_csqr += cre**2. + cim**2.
		
		# Get sum of squre of the coefficients 'csqr'
		# Get square root of 'csqr' --> 'nsqr' : for normalisation
		csqr = up_csqr + dn_csqr
		nsqr = np.sqrt(csqr)

		#
		# normalise
		#
		for basis in lumo_evecs[_state]:
			#
			# UPDATE NORMALISED BASIS SET COEFFICIENT
			basis['c_real'] = basis['c_real'] / nsqr
			basis['c_imag'] = basis['c_imag'] / nsqr

#print(f" * ---------------------------------------------")
print(f" * Eigenvectors normalisation completed")
print(f" * ---------------------------------------------")


#
# Retrieving relavent basis occupantion
#

#
# No classification for up/dn spin states
#

# for selected states : homo_states list<int>  / lumo_states list<int>
# target variables    : homo_evecs[state<int>] / lumo_evecs[state<int>] --> basis set normalised

_homo_state_occ = {}	# attr :: save
_lumo_state_occ = {}	# attr :: save
print(f" *")
print(f" *")
print(f" *")
print(f" *")
print(f" * ---------------------------------------------")
print(f" * Selected HOMO state decomposition")
print(f" * ---------------------------------------------")
# looping selected homo states
for _state in homo_states:

	# check if state exists
	if _state in homo_evecs.keys():

		_Au_s  = 0.	# 6s      : tmp
		_Au_p  = 0.	# 6p      : tmp
		_Au_d  = 0.	# 5d      : tmp
		_S_p   = 0.	# 3p      : tmp
		_O     = 0.	# others  : tmp

		t_up_csqr = 0.	# logging up channel
		t_dn_csqr = 0.	# logging dn channel

		_homo_state_occ[_state] = {}	# create state - occ entry

		# get evec info from the '_state' and looping
		for basis in homo_evecs[_state]:
			# {'basis_no': 1, 'atom_no': 1, 'type': 'atomic', 'n': 1, 'l': 's', 'm': 0, 'spin': 'up', 'c_real': -3.867159854e-06, 'c_imag': -2.1400239085e-05}
			atom_no = basis['atom_no']
			c_real  = basis['c_real']
			c_imag  = basis['c_imag']
			#print(f"{atom_no:4d}{atomlist[atom_no]:6s}{basis['type']:8s}{basis['n']:2d}{basis['l']:3s}{basis['m']:3d} {basis['spin']:4s} \
			#			{basis['c_real']:12.8f}{basis['c_imag']:12.8f}")
			# contents check

			# Au
			if atomlist[atom_no] == 'Au':
				if basis['n'] == 5 and basis['l'] == 'd':	# get Au 5d
					_Au_d += c_real**2. + c_imag**2.
				elif basis['n'] == 6 and basis['l'] == 's':	# get Au 6s
					_Au_s += c_real**2. + c_imag**2.
				elif basis['n'] == 6 and basis['l'] == 'p':	# get Au 6p
					_Au_p += c_real**2. + c_imag**2.
				else:
					_O += c_real**2. + c_imag**2.
			# S
			elif atomlist[atom_no] == 'S':
				if basis['n'] == 3 and basis['l'] == 'p':	# get S 3p
					_S_p += c_real**2. + c_imag**2.
				else:
					_O += c_real**2. + c_imag**2.
			else:
				_O += c_real**2. + c_imag**2.

			#
			# Logging up/dn spin states
			#

			# up state
			if basis['spin'] == 'up':
			    cre = basis['c_real']
			    cim = basis['c_imag']
			    t_up_csqr += cre**2. + cim**2.
			# dn state
			if basis['spin'] == 'dn':
			    cre = basis['c_real']
			    cim = basis['c_imag']
			    t_dn_csqr += cre**2. + cim**2.

		_homo_state_occ[_state]['state']   = _state
		_homo_state_occ[_state]['eval']    = soc_eval[_state]['eval']
		_homo_state_occ[_state]['soc_eval']= soc_eval[_state]['soc_eval']
		_homo_state_occ[_state]['Au_d']    = _Au_d
		_homo_state_occ[_state]['Au_sp']   = _Au_s + _Au_p
		_homo_state_occ[_state]['S_p']     = _S_p
		_homo_state_occ[_state]['O']       = _O
		_homo_state_occ[_state]['occ_sum'] = _Au_d + _Au_s + _Au_p + _S_p + _O
		_homo_state_occ[_state]['up_frac'] = t_up_csqr
		_homo_state_occ[_state]['dn_frac'] = t_dn_csqr

		# contents check
		#print(f' * state: {_state}:', _homo_state_occ[_state])
		'''
			Data Structure Example:

			_homo_state_occ[state<int>] = {
											'state': 3101,
											'eval': -6.819686,
											'soc_eval': -6.744122,
											'Au_d': 0.3340681572601996,
											'Au_sp': 0.10499049652114065,
											'S_p': 0.4308686922093148,
											'O': 0.1300726540093463,
											'occ_sum': 1.0000000000000013,
											'up_frac': 0.8253866306940105,
											'dn_frac': 0.17461336930598895
											}
		'''

print(f" * ---------------------------------------------")
print(f" * Selected LUMO state decomposition")
print(f" * ---------------------------------------------")
# looping selected lumo states
for _state in lumo_states:

	# check if state exists
	if _state in lumo_evecs.keys():

		_Au_s  = 0.	# 6s      : tmp
		_Au_p  = 0.	# 6p      : tmp
		_Au_d  = 0.	# 5d      : tmp
		_S_p   = 0.	# 3p      : tmp
		_O     = 0.	# others  : tmp

		t_up_csqr = 0.	# logging up channel
		t_dn_csqr = 0.	# logging dn channel

		_lumo_state_occ[_state] = {}	# create state - occ entry

		# get evec info from the '_state' and looping
		for basis in lumo_evecs[_state]:
			# {'basis_no': 1, 'atom_no': 1, 'type': 'atomic', 'n': 1, 'l': 's', 'm': 0, 'spin': 'up', 'c_real': -3.867159854e-06, 'c_imag': -2.1400239085e-05}
			atom_no = basis['atom_no']
			c_real  = basis['c_real']
			c_imag  = basis['c_imag']
			#print(f"{atom_no:4d}{atomlist[atom_no]:6s}{basis['type']:8s}{basis['n']:2d}{basis['l']:3s}{basis['m']:3d} {basis['spin']:4s} \
			#			{basis['c_real']:12.8f}{basis['c_imag']:12.8f}")
			# contents check

			# Au
			if atomlist[atom_no] == 'Au':
				if basis['n'] == 5 and basis['l'] == 'd':	# get Au 5d
					_Au_d += c_real**2. + c_imag**2.
				elif basis['n'] == 6 and basis['l'] == 's':	# get Au 6s
					_Au_s += c_real**2. + c_imag**2.
				elif basis['n'] == 6 and basis['l'] == 'p':	# get Au 6p
					_Au_p += c_real**2. + c_imag**2.
				else:
					_O += c_real**2. + c_imag**2.
			# S
			elif atomlist[atom_no] == 'S':
				if basis['n'] == 3 and basis['l'] == 'p':	# get S 3p
					_S_p += c_real**2. + c_imag**2.
				else:
					_O += c_real**2. + c_imag**2.
			else:
				_O += c_real**2. + c_imag**2.

			#
			# Logging up/dn spin states
			#

			# up state
			if basis['spin'] == 'up':
			    cre = basis['c_real']
			    cim = basis['c_imag']
			    t_up_csqr += cre**2. + cim**2.
			# dn state
			if basis['spin'] == 'dn':
			    cre = basis['c_real']
			    cim = basis['c_imag']
			    t_dn_csqr += cre**2. + cim**2.

		_lumo_state_occ[_state]['state']   = _state
		_lumo_state_occ[_state]['eval']    = soc_eval[_state]['eval']
		_lumo_state_occ[_state]['soc_eval']= soc_eval[_state]['soc_eval']
		_lumo_state_occ[_state]['Au_d']    = _Au_d
		_lumo_state_occ[_state]['Au_sp']   = _Au_s + _Au_p
		_lumo_state_occ[_state]['S_p']     = _S_p
		_lumo_state_occ[_state]['O']       = _O
		_lumo_state_occ[_state]['occ_sum'] = _Au_d + _Au_s + _Au_p + _S_p + _O
		_lumo_state_occ[_state]['up_frac'] = t_up_csqr
		_lumo_state_occ[_state]['dn_frac'] = t_dn_csqr

		# contents check
		#print(f' * state: {_state}:', _lumo_state_occ[_state])
		'''
			Data Structure Example:

			_lumo_state_occ[state<int>] = {
											'state': 3101,
											'eval': -6.819686,
											'soc_eval': -6.744122,
											'Au_d': 0.3340681572601996,
											'Au_sp': 0.10499049652114065,
											'S_p': 0.4308686922093148,
											'O': 0.1300726540093463,
											'occ_sum': 1.0000000000000013,
											'up_frac': 0.8253866306940105,
											'dn_frac': 0.17461336930598895
											}
		'''

#
# Write HOMO / LUMO (Selected) eigenvectors
#

print(f" * ---------------------------------------------")
print(f" * writing processed occupancy file ...",end="")

_homo_occ_file_p = 'homo_occ.json'
_lumo_occ_file_p = 'lumo_occ.json'
with open(_homo_occ_file_p,'w') as f1, open(_lumo_occ_file_p,'w') as f2:
	json.dump(_homo_state_occ,f1,indent=4)
	json.dump(_lumo_state_occ,f2,indent=4)
print(f" finished")
print(f" * ---------------------------------------------")

#
# Processing Integral (transition)
#
#cube_001_eigenstate_03100_spin_1.cube     
#cube_002_eigenstate_imag_03100_spin_1.cube
#cube_003_eigenstate_03100_spin_2.cube     
#cube_004_eigenstate_imag_03100_spin_2.cube 
#for i in range(1, 81):
#    print(str(i).zfill(3))
# HOMO 3109
# homo_states = []
# lumo_states = []

homo_cube_files = []
lumo_cube_files = []
_n = 1


print(f" * ---------------------------------------------")
print(f' * SOC-HOMO state cube files')
print(f" * ---------------------------------------------")
for i in range(homo_states[0],homo_states[-1]+1):
	up_real = 'cube_'+str(_n).zfill(3)+'_eigenstate_'+str(i).zfill(5)+'_spin_1.cube'
	_n += 1
	up_imag = 'cube_'+str(_n).zfill(3)+'_eigenstate_imag_'+str(i).zfill(5)+'_spin_1.cube'
	_n += 1
	dn_real = 'cube_'+str(_n).zfill(3)+'_eigenstate_'+str(i).zfill(5)+'_spin_2.cube'
	_n += 1
	dn_imag = 'cube_'+str(_n).zfill(3)+'_eigenstate_imag_'+str(i).zfill(5)+'_spin_2.cube'
	_n += 1
	
	tmp = [ up_real, up_imag, dn_real, dn_imag ]

	for item in tmp:
		path = os.path.join(os.getcwd(),item)
		if not os.path.exists(path):
			print(f'ERROR FILE NOT FOUND : {item}')

	homo_cube_files.append(tmp)
	print(tmp)

print(f" * ---------------------------------------------")
print(f' * SOC-LUMO state cube files')
print(f" * ---------------------------------------------")
for i in range(lumo_states[0],lumo_states[-1]+1):
	up_real = 'cube_'+str(_n).zfill(3)+'_eigenstate_'+str(i).zfill(5)+'_spin_1.cube'
	_n += 1
	up_imag = 'cube_'+str(_n).zfill(3)+'_eigenstate_imag_'+str(i).zfill(5)+'_spin_1.cube'
	_n += 1
	dn_real = 'cube_'+str(_n).zfill(3)+'_eigenstate_'+str(i).zfill(5)+'_spin_2.cube'
	_n += 1
	dn_imag = 'cube_'+str(_n).zfill(3)+'_eigenstate_imag_'+str(i).zfill(5)+'_spin_2.cube'
	_n += 1

	tmp = [ up_real, up_imag, dn_real, dn_imag ]

	for item in tmp:
		path = os.path.join(os.getcwd(),item)
		if not os.path.exists(path):
			print(f'ERROR FILE NOT FOUND : {item}')

	lumo_cube_files.append(tmp)
	print(tmp)

#
# Calculating Transition Moments
#
print(f' * SOC Transition calculation')
print(f" * ---------------------------------------------")
print(f' * istate    soc_eval    fstate    soc_eval     transInt    transMoment')
print(f" * ---------------------------------------------")
for i in range(homo_states[0],homo_states[-1]+1):
	for f in range(lumo_states[0],lumo_states[-1]+1):

		# contents check
		#print(f' istate/fstate : {i} / {f}')
		#print(f' istate eval   : {soc_eval[i]}')	# print dict : {'occ': 1.0, 'eval': -6.882954, 'soc_eval': -6.777501} -- state 3100
		#print(f' fstate eval   : {soc_eval[f]}')
		#print(f' istate cubes  : {homo_cube_files[i-homo_states[0]]}')
		#print(f' fstate cubes  : {lumo_cube_files[f-lumo_states[0]]}')

		istate = i
		fstate = f
		istate_info = soc_eval[i]
		fstate_info = soc_eval[f]

		istate_cubelist = homo_cube_files[i-homo_states[0]]
		fstate_cubelist = lumo_cube_files[f-lumo_states[0]]

		transInt, transMoment = get_trans_int_full(istate_cubelist,fstate_cubelist)
		print(f"{istate:10d}{istate_info['soc_eval']:12.6f}{fstate:10d}{fstate_info['soc_eval']:12.6f}\t{transInt:16.9f}\t{transMoment}")

#   0  50 100 150 200 250      3100   -6.777501      3110   -5.422019 278690.827702474  (array([-426.73186855,   -0.91900678,  -19.9012674 ]), array([-300.3769296 ,   50.47157911,  -58.48209054]))
# END ---
