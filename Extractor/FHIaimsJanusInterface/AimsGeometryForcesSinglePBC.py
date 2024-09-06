#
# 08.24 WKJEE
#
import sys,os
import numpy as np
import json

_aims_single_out_file = sys.argv[1]
try:
	_outfile = sys.argv[2] + '.json'
except:
	_outfile = 'force.json'

with open(_aims_single_out_file,'r') as f:

	_noa = 0
	_lvecs = [ None for _ in range(3) ]
	_atomlist = []
	_fraclist = []

	# Get Number Of Atoms
	for line in f:
		if 'Number of atoms' in line:
			_noa = int(line.strip().split()[5])

	f.seek(0)

	# Get Geometry
	for line in f:
		if 'in the first line of geometry.in' in line:

			f.readline()
			f.readline()

			l = f.readline().strip().split()
			_lvecs[0] = [ float(l[i+1]) for i in range(3) ]
			l = f.readline().strip().split()
			_lvecs[1] = [ float(l[i+1]) for i in range(3) ]
			l = f.readline().strip().split()
			_lvecs[2] = [ float(l[i+1]) for i in range(3) ]

			_lvecs = np.array(_lvecs)

			for i in range(_noa):

				atom = f.readline().strip().split()
				_atomlist.append(atom[4])
				_fraclist.append([ float(atom[i+1]) for i in range(3) ])

			break

	f.seek(0)

	_stress_tensor = None	   # [eV]: xx, yy, zz, xy, xz, yz
	_stress_tensor_sym = None  # [eV/Å**3]
	_forcelist = []            # [eV/Å]
	# Get SCF converged Forces / Stress
	for line in f:
		if 'Self-consistency cycle converged' in line:

			while True:
				l = f.readline()

				if 'Sum of all contributions        :' in l:
					#_stress_tensor = [ float(l.strip().split()[5:][i]) for i in range(6) ]
					_stress_tensor = np.array(l.strip().split()[5:],dtype=np.float64)
					#print(_stress_tensor)
					break

			while True:
				l = f.readline()

				if 'Analytical stress tensor - Symmetrized' in l:
					f.readline()
					f.readline()
					f.readline()
					f.readline()

					stmp1 = f.readline().strip().split()[2:-1]
					stmp2 = f.readline().strip().split()[2:-1]
					stmp3 = f.readline().strip().split()[2:-1]

					_stress_tensor_sym = np.array([stmp1,stmp2,stmp3],dtype=np.float64)
		
					#print(_stress_tensor_sym)
					break

			while True:
				l = f.readline()
				
				if 'Total atomic forces' in l:
					for i in range(_noa):
						_forcelist.append(f.readline().strip().split()[2:])

					_forcelist = np.array(_forcelist,dtype=np.float64)

					break

#
# Summary of Obtained Items
#
'''
	_noa				# Number of Atoms
	_atomlist			# Species Name List
	_lvecs				# lattice vectors
	_fraclist			# Atom Fractional List
	_stress_tensor		# standard [xx,yy,zz,xy,xz,yz] - [eV]
	_stress_tensor_sym	# symmetrized 3 x 3 - [eV/Å**3]
	_forcelist			# atomic force [eV/Å]
'''

# OUTPUT CHECKER
#print(_noa)
#print(_lvecs)
#for atom,frac in zip(_atomlist,_fraclist):
#	print(atom,frac)
#
#print(_stress_tensor)
#print(_stress_tensor_sym)
#print(_forcelist)

#
# Output write
#
data = {}
data['lattice_vectors'] = _lvecs.tolist()					# 2d list 3 x 3
data['atomlist'] = _atomlist								# 1d list
data['fraclist'] = _fraclist								# 2d list n x 3 (n: number of atoms, same order with atomlist)
data['stress_tensor'] = _stress_tensor.tolist()				# 1d list 6     (xx,yy,zz,xy,xz,yz in [eV])
data['stress_tensor_sym'] = _stress_tensor_sym.tolist()		# 2d list 3 x 3 (in [eV/Å**3])
data['forcelist'] = _forcelist.tolist()						# 2d list n x 3 (n: number of atoms, same order with atomlist)

with open(_outfile,'w') as f:
	json.dump(data,f,indent=4)

# keys
'''
	lattice_vectors
	atomlist
	fraclist
	forcelist
	stress_tensor
	stress_tensor_sym
'''



