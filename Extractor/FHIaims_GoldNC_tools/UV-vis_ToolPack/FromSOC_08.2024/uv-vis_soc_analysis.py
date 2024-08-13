#
#	UV-VIS FHIaims analyser
#
#	07.2024 WKJEE
#
import numpy as np
import sys,os

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
_scan_range = 8
#_bottom = 8	# obtain HOMO-7 ... HOMO+0
#_top    = 8 # obtain LUMO+0 ... LUMO+7

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

print(f" * list of selected states : soc-evals (eV)")
print(f" * ---------------------------------------------")
#
# GET HOMO SOC-STATE EVALS
for key in soc_eval.keys():
	if key in homo_states:
		print(f" [h] state/eval : {key:6d}{soc_eval[key]['soc_eval']:20.12f}")
#
# GET LUMO SOC-STATE EVALS
for key in soc_eval.keys():
	if key in lumo_states:
		print(f" [l] state/eval : {key:6d}{soc_eval[key]['soc_eval']:20.12f}")
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

# looping selected homo states
for _state in homo_states:

	# check if state exists
	if _state in homo_evecs.keys():

		_Au_s  = 0.	# 6s      : tmp
		_Au_p  = 0.	# 6p      : tmp
		_Au_d  = 0.	# 5d      : tmp
		_S_p   = 0.	# 3p      : tmp
		_O     = 0.	# others  : tmp

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

			t_up_csqr = 0.
			t_dn_csqr = 0.

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
			t_csqr = t_up_csqr + t_dn_csqr

			#
			# t_up_csqr : up portion
			# t_dn_csqr : dn portion
			#
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

		print(f' * state: {_state}:', _homo_state_occ[_state])

		#sys.exit(1)

# END ---
