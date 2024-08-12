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

if _state in homo_evecs.keys():
	for basis in homo_evecs[_state]:
# POSSIBLE OUTPUT : {'basis_no': 1, 'atom_no': 1, 'type': 'atomic', 'n': 1, 'l': 's', 'm': 0, 'spin': 'up', 'c_real': -3.867159854e-06, 'c_imag': -2.1400239085e-05}
		print(basis)

#
# saving attrs
#

for state in homo_states:

	_state = state

	up_csqr = 0.
	dn_csqr = 0.
	csqr = 0.

	t_up_csqr = 0.
	t_dn_csqr = 0.
	t_csqr = 0.

	if _state in homo_evecs.keys():

		#
		# get normalise factor
		for basis in homo_evecs[_state]:
			# 'up'
			if basis['spin'] == 'up':
				cre = basis['c_real']
				cim = basis['c_imag']
				up_csqr += cre**2. + cim**2.
			# 'dn'
			if basis['spin'] == 'dn':
				cre = basis['c_real']
				cim = basis['c_imag']
				dn_csqr += cre**2. + cim**2.

		csqr = up_csqr + dn_csqr
		nsqr = np.sqrt(csqr)

		print(f" * no normalisation ------------- ")
		print(f" {_state} <--- state")
		print(f" up_csqr : {up_csqr:20.12f}")
		print(f" dn_csqr : {dn_csqr:20.12f}")
		print(f" csqr    : {csqr:20.12f}")
			
		#
		# normalise
		for basis in homo_evecs[_state]:

			basis['c_real'] = basis['c_real'] / nsqr
			basis['c_imag'] = basis['c_imag'] / nsqr


		for basis in homo_evecs[_state]:
			# up
			if basis['spin'] == 'up':
				cre = basis['c_real']
				cim = basis['c_imag']
				t_up_csqr += cre**2. + cim**2.
			# dn
			if basis['spin'] == 'dn':
				cre = basis['c_real']
				cim = basis['c_imag']
				t_dn_csqr += cre**2. + cim**2.

		t_csqr = t_up_csqr + t_dn_csqr
		print(f" *    normalisation ------------- ")
		print(f" {_state} <--- state")
		print(f" up_csqr : {t_up_csqr:20.12f}")
		print(f" dn_csqr : {t_dn_csqr:20.12f}")
		print(f" csqr    : {t_csqr:20.12f}")

		
		print(f" * weight *")
		print(f" up/dn : {t_up_csqr:12.6f}/{t_dn_csqr:12.5f}")


# END ---


'''
	Possible Output:
 * no normalisation ------------- 
 3101 <--- state
 up_csqr :       1.009216456080
 dn_csqr :       0.213503198625
 csqr    :       1.222719654705
 *    normalisation ------------- 
 3101 <--- state
 up_csqr :       0.825386630694
 dn_csqr :       0.174613369306
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.825387/     0.17461
 * no normalisation ------------- 
 3102 <--- state
 up_csqr :       0.252293226024
 dn_csqr :       0.972459734120
 csqr    :       1.224752960144
 *    normalisation ------------- 
 3102 <--- state
 up_csqr :       0.205995195957
 dn_csqr :       0.794004804043
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.205995/     0.79400
 * no normalisation ------------- 
 3103 <--- state
 up_csqr :       1.077425346185
 dn_csqr :       0.134325853585
 csqr    :       1.211751199770
 *    normalisation ------------- 
 3103 <--- state
 up_csqr :       0.889147331886
 dn_csqr :       0.110852668114
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.889147/     0.11085
 * no normalisation ------------- 
 3104 <--- state
 up_csqr :       0.152214199784
 dn_csqr :       1.044762685421
 csqr    :       1.196976885205
 *    normalisation ------------- 
 3104 <--- state
 up_csqr :       0.127165529815
 dn_csqr :       0.872834470185
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.127166/     0.87283
 * no normalisation ------------- 
 3105 <--- state
 up_csqr :       0.949372813230
 dn_csqr :       0.246060203231
 csqr    :       1.195433016461
 *    normalisation ------------- 
 3105 <--- state
 up_csqr :       0.794166465337
 dn_csqr :       0.205833534663
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.794166/     0.20583
 * no normalisation ------------- 
 3106 <--- state
 up_csqr :       0.207843333392
 dn_csqr :       0.961935359056
 csqr    :       1.169778692449
 *    normalisation ------------- 
 3106 <--- state
 up_csqr :       0.177677482702
 dn_csqr :       0.822322517298
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.177677/     0.82232
 * no normalisation ------------- 
 3107 <--- state
 up_csqr :       1.086243571866
 dn_csqr :       0.113808589051
 csqr    :       1.200052160916
 *    normalisation ------------- 
 3107 <--- state
 up_csqr :       0.905163631418
 dn_csqr :       0.094836368582
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.905164/     0.09484
 * no normalisation ------------- 
 3108 <--- state
 up_csqr :       0.036772109311
 dn_csqr :       1.168368181318
 csqr    :       1.205140290629
 *    normalisation ------------- 
 3108 <--- state
 up_csqr :       0.030512720881
 dn_csqr :       0.969487279119
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.030513/     0.96949
 * no normalisation ------------- 
 3109 <--- state
 up_csqr :       1.193423566196
 dn_csqr :       0.036636672967
 csqr    :       1.230060239164
 *    normalisation ------------- 
 3109 <--- state
 up_csqr :       0.970215545710
 dn_csqr :       0.029784454290
 csqr    :       1.000000000000
 * weight *
 up/dn :     0.970216/     0.02978
'''




