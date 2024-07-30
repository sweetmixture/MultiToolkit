#!/bin/python
'''
    Author  :   wkjee
    Title   :   OutputParser

    Layout

    /root
        /Base
            Atoms.py    : Atom, Shell
            Clusters.py : Cluster
            Cells.py    : Cell
		/Extractor
		  *	GULP.py		: GULP_Patterns, ExtractGULP
			FHIaims.py	: FHIaims_Patterns, ExtractFHIaims

    19.09.2023  : framework
'''

import os
import numpy as np

from Base.Cells import Cell
#
# True/False <-- isnumber(token<str>)
#
def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

class GULP_Patterns(object):

	def __init__(self):

		'''
			20.09.2023 update
		'''

		self.Generic = {
			'JobDone'       : { 'space' : 0, 'next' : 0, 'loc' : 0, 'pattern' : 'Job Finished at' },
		}

		# for Input
		self.InputConfig = {
			'From'			: { 'space' : 0, 'next' : 0, 'loc' : 0, 'pattern' : 'Input for Configuration' },
			'IrAtomsShells' : { 'space' : 0, 'next' : 0, 'loc' : 6, 'pattern' : 'Number of irreducible atoms/shells =' },
			'AtomsShells'   : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Total number atoms/shells =' },
			'Dimension'     : { 'space' : 0, 'next' : 0, 'loc' : 3, 'pattern' : 'Dimensionality =' },

			'InitEnergy'    : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Total lattice energy' },										
			'InitFrac'      : { 'space' : 5, 'next' : 0, 'loc' : 0, 'pattern' : 'Fractional coordinates of'},
			'LattVectors'   : { 'space' : 1, 'next' : 3, 'loc' : 0, 'pattern' : 'Cartesian lattice vectors (Angstroms) :' },
			'LattParams'    : { 'space' : 1, 'next' : 3, 'loc' : 0, 'pattern' : 'Cell parameters (Angstroms/Degrees):' },
			'LattVol'       : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Initial cell volume =' },

			# Init Energy Decomposition
			'InitEnergyIP'         : { 'space' : 0, 'next' : 0, 'loc' : 4, 'pattern' : 'Interatomic potentials     ='},
			'InitEnergyElecRe'     : { 'space' : 0, 'next' : 0, 'loc' : 6, 'pattern' : 'Monopole - monopole (real) ='},
			'InitEnergyElecIm'     : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Monopole - monopole (recip)='},
			'InitEnergyElec'       : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Monopole - monopole (total)='},
		}
		#
		#	Note. 'space' tells how many lines for skipping to get actual information
		#	      'next'  expected length of the string if: len(line.split())
		#	      'loc'   index where the information is: line.split()[loc]

		# for output
		self.OutputConfig = {
			'From'          : { 'space' : 0, 'next' : 0, 'loc' : 0, 'pattern' : 'Output for configuration' },
			'InitEnergy'    : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Total lattice energy' },										
			'FinalEnergy'   : { 'space' : 0, 'next' : 0, 'loc' : 4, 'pattern' : 'Final energy =' },
			'FinalGnorm'    : { 'space' : 0, 'next' : 0, 'loc' : 4, 'pattern' : 'Final Gnorm  =' },
			'FinalFrac'     : { 'space' : 5, 'next' : 0, 'loc' : 0, 'pattern' : 'Final fractional coordinates of atoms :' },
			'LattVectors'   : { 'space' : 1, 'next' : 3, 'loc' : 0, 'pattern' : 'Final Cartesian lattice vectors (Angstroms) :' },
			'LattParams'    : { 'space' : 2, 'next' : 6, 'loc' : 0, 'pattern' : 'Final cell parameters and derivatives :' },
			'LattVol'       : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Non-primitive cell volume =' },

			# Final Energy Decomposition
			'FinalEnergyIP'         : { 'space' : 0, 'next' : 0, 'loc' : 4, 'pattern' : 'Interatomic potentials     ='},
			'FinalEnergyElecRe'     : { 'space' : 0, 'next' : 0, 'loc' : 6, 'pattern' : 'Monopole - monopole (real) ='},
			'FinalEnergyElecIm'     : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Monopole - monopole (recip)='},
			'FinalEnergyElec'       : { 'space' : 0, 'next' : 0, 'loc' : 5, 'pattern' : 'Monopole - monopole (total)='},
		}
		'''
			need keyword check / dimension check
		'''
		self.Property = {
			'keyword'       : { 'space' : 0, 'next' : 0, 'loc' : 0, 'pattern' : 'property' },
			'ElaConst'      : { 'space' : 4, 'next' : 6, 'loc' : 0, 'pattern' : 'Elastic Constant Matrix: (Units=GPa)' },
			'ElaComp'       : { 'space' : 4, 'next' : 6, 'loc' : 0, 'pattern' : 'Elastic Compliance Matrix: (Units=1/GPa)' },
			'BulkMod'       : { 'space' : 0, 'next' : 0, 'loc' : 0, 'pattern' : 'Bulk  Modulus (GPa)     =' },
			'ShearMod'      : { 'space' : 0, 'next' : 0, 'loc' : 0, 'pattern' : 'Shear Modulus (GPa)     =' },
			'Compress'      : { 'space' : 0, 'next' : 0, 'loc' : 4, 'pattern' : 'Compressibility (1/GPa) =' },
			'YoungsMod'     : { 'space' : 0, 'next' : 0, 'loc' : 0, 'pattern' : 'Youngs Moduli (GPa)     =' },
			'StaticDielec'  : { 'space' : 4, 'next' : 3, 'loc' : 0, 'pattern' : 'Static dielectric constant tensor :' },
			'HighDielec'    : { 'space' : 4, 'next' : 3, 'loc' : 0, 'pattern' : 'High frequency dielectric constant tensor :' },
		}

class ExtractGULP(GULP_Patterns):

	def __init__(self):
		super().__init__()	# load patterns

		# FLAGS : LOGICALS
		self.__FileNormal = False
		self.__FinishNormal = False

		self.output_file = None
		self.output_file_ptr = None

		# PARAMETERS
		self.__gnorm_tol = 1.E-3	# 0.001

	def reset(self):

		if self.__FileNormal:
			self.output_file_ptr.close()
			self.output_file_ptr = None
			self.output_file = None

		self.__FileNormal = False
		self.__FinishNormal = False

	'''
		setters
	'''
	def set_output_file(self,output):

		# Only does file-check : __FileNormal
		try:
			self.output_file = output
			self.output_file_ptr = open(self.output_file,'r')
			self.__FileNormal = True
			return True
		except Exception as e:
			self.output_file_ptr = None
			self.__FileNormal = False
			return False

	# --------------------------------------------------------------------------------------------------------------------
	def check_finish_normal(self):
		if self.__FileNormal:
			for line in self.output_file_ptr:
				if self.Generic['JobDone']['pattern'] in line:
					self.__FinishNormal = True
					self.output_file_ptr.seek(0)
					return True
			# end for
			self.output_file_ptr.seek(0)
			return False
		else:
			return False

	# status check internal use only
	def check_status(self):
		return [ self.__FileNormal, self.__FinishNormal ]

	'''
		Data Extraction Methods

		Output Convention : [ True/False , Return <method dependent format> ]
	'''
	# --------------------------------------------------------------------------------------------------------------------
	def get_initial_energy(self):

		if False in self.check_status():
			return False, None

		for line in self.output_file_ptr:
			if self.InputConfig['InitEnergy']['pattern'] in line:
				energy = float(line.strip().split()[self.OutputConfig['InitEnergy']['loc']-1])
				self.output_file_ptr.seek(0)
				return True, energy

		# end for
		self.output_file_ptr.seek(0)
		return False, None

	def get_initial_energy_full(self):

		energy_list = []

		if False in self.check_status():
			return False, None

		for line in self.output_file_ptr:
			if self.InputConfig['InitEnergyIP']['pattern'] in line:
				energy = float(line.strip().split()[self.InputConfig['InitEnergyIP']['loc']-1])
				#self.output_file_ptr.seek(0)
				break

		energy_list.append(energy) # update (1) IP

		for line in self.output_file_ptr:
			if self.InputConfig['InitEnergyElecRe']['pattern'] in line:
				energy = float(line.strip().split()[self.InputConfig['InitEnergyElecRe']['loc']-1])
				#self.output_file_ptr.seek(0)
				break

		energy_list.append(energy) # update (2) Ewald Real

		for line in self.output_file_ptr:
			if self.InputConfig['InitEnergyElecIm']['pattern'] in line:
				energy = float(line.strip().split()[self.InputConfig['InitEnergyElecIm']['loc']-1])
				#self.output_file_ptr.seek(0)
				break

		energy_list.append(energy) # update (3) Ewald Imag

		for line in self.output_file_ptr:
			if self.InputConfig['InitEnergyElec']['pattern'] in line:
				energy = float(line.strip().split()[self.InputConfig['InitEnergyElec']['loc']-1])
				self.output_file_ptr.seek(0)

				energy_list.append(energy)
				# if_success : return here
				return True, energy_list

		# end for
		self.output_file_ptr.seek(0)
		return False, None

	# --------------------------------------------------------------------------------------------------------------------

	def get_initial_frac(self):
		NotImplemented

	# --------------------------------------------------------------------------------------------------------------------
	def get_initial_frac_cosh(self):	# get core-shell (cosh)
		
		#
		# check if gulp run status: check_status()<list[2]> : updated by 'ExtractGULP.check_finish_normal()'
		#
		if False in self.check_status():
			return False, None
		
		pattern = False
		atomlist = []

		for line in self.output_file_ptr:
			if self.InputConfig['InitFrac']['pattern'] in line:
				pattern = True
				break
		
		if pattern:

			iterator = iter(self.output_file_ptr)

			#
			# skipping 'self.InputConfig['InitFrac']['space']' number of lines
			#
			for i in range(self.InputConfig['InitFrac']['space']):
				next(iterator)

			while True:

				strings = next(iterator).split()

				if len(strings) < 7:
				# e.g., string will be like '1  Tc    c     0.717584    0.345205    0.421269    0.000000' --> 7 letters
					break

				# strings[1] reserved for species
				atype = None
				if strings[2] == 'c':
					atype = 'core'
				if strings[2] == 's':
					atype = 'shel'
				# get frac
				frac = []
				for token in strings:

					if is_number(token):
						frac.append(float(token))
					# check
					#print(frac,token,token.isdigit(),token.isnumeric(),token.isdecimal(),is_number(token))
					if len(frac) == 4:
						break
				atom = [ strings[1], atype, frac[1], frac[2], frac[3] ]
				atomlist.append(atom)

			self.output_file_ptr.seek(0)
			return True, atomlist

		else: 
			self.output_file_ptr.seek(0)
			return False, None

	# --------------------------------------------------------------------------------------------------------------------
	def get_initial_lvectors(self):

		if False in self.check_status():
			return False, None

		pattern = False
		lvectors = []

		for line in self.output_file_ptr:
			if self.InputConfig['LattVectors']['pattern'] in line:
				pattern = True
				break

		if pattern:

			iterator = iter(self.output_file_ptr)
			next(iterator)

			lvectors.append(next(iterator).split())	
			lvectors.append(next(iterator).split())	
			lvectors.append(next(iterator).split())	

			for i in range(3):
				for j in range(3):
					lvectors[i][j] = float(lvectors[i][j])

			self.output_file_ptr.seek(0)
			return True, lvectors

		else:
			self.output_file_ptr.seek(0)
			return False, None

	# --------------------------------------------------------------------------------------------------------------------
	def get_initial_lparams(self):
		NotImplemented
	def get_initial_lvolume(self):
		NotImplemented
	# --------------------------------------------------------------------------------------------------------------------
	def get_final_energy(self):

		if False in self.check_status():
			return False, None

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalEnergy']['pattern'] in line:
				energy = float(line.strip().split()[self.OutputConfig['FinalEnergy']['loc']-1])
				self.output_file_ptr.seek(0)
				return True, energy

		# end for
		self.output_file_ptr.seek(0)
		return False, None

	#
	#	For getting lattice energy : (1) IP (2) Elec-Re (3) Elec-Im (4) Elec
	#
	def get_final_energy_full(self):

		energy_list = []

		if False in self.check_status():
			return False, None

		#	First, get to the end of optimisation
		for line in self.output_file_ptr:
			if self.OutputConfig['FinalEnergyIP']['pattern'] in line:
				break

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalEnergyIP']['pattern'] in line:
				energy = float(line.strip().split()[self.OutputConfig['FinalEnergyIP']['loc']-1])
				#self.output_file_ptr.seek(0)
				break

		energy_list.append(energy) # update (1) IP

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalEnergyElecRe']['pattern'] in line:
				energy = float(line.strip().split()[self.OutputConfig['FinalEnergyElecRe']['loc']-1])
				#self.output_file_ptr.seek(0)
				break

		energy_list.append(energy) # update (2) Ewald Real

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalEnergyElecIm']['pattern'] in line:
				energy = float(line.strip().split()[self.OutputConfig['FinalEnergyElecIm']['loc']-1])
				#self.output_file_ptr.seek(0)
				break

		energy_list.append(energy) # update (3) Ewald Imag

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalEnergyElec']['pattern'] in line:
				energy = float(line.strip().split()[self.OutputConfig['FinalEnergyElec']['loc']-1])
				self.output_file_ptr.seek(0)

				energy_list.append(energy)
				# if_success : return here
				return True, energy_list

		# end for
		self.output_file_ptr.seek(0)
		return False, None
	# --------------------------------------------------------------------------------------------------------------------
	def get_final_gnorm(self,gnorm_tol=None):

		if False in self.check_status():
			return False, None
		if gnorm_tol is None:
			gnorm_tol = self.__gnorm_tol

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalGnorm']['pattern'] in line:
				try:
					gnorm = float(line.strip().split()[self.OutputConfig['FinalGnorm']['loc']-1])
				except:
					gnorm = 9999.
				self.output_file_ptr.seek(0)

				if gnorm < gnorm_tol:
					return True, gnorm
				else:
					return False, None
		# end for
		self.output_file_ptr.seek(0)
		return False, None
	# --------------------------------------------------------------------------------------------------------------------
	def get_final_frac(self):
		
		#
		# check if gulp run status: check_status()<list[2]> : updated by 'ExtractGULP.check_finish_normal()'
		#
		if False in self.check_status():
			return False, None
		
		pattern = False
		atomlist = []

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalFrac']['pattern'] in line:
				pattern = True
				break
		
		if pattern:

			iterator = iter(self.output_file_ptr)

			#
			# skipping 'self.OutputConfig['FinalFrac']['space']' number of lines
			#
			for i in range(self.OutputConfig['FinalFrac']['space']):
				next(iterator)

			while True:

				strings = next(iterator).split()
				if len(strings) < 7:
				# e.g., string will be like '1  Tc    c     0.717584    0.345205    0.421269    0.000000' --> 7 letters
					break
				if strings[2] == 'c':		# if this is core
					atom = [ strings[1], float(strings[3]), float(strings[4]), float(strings[5]) ]
					atomlist.append(atom)

			self.output_file_ptr.seek(0)
			return True, atomlist

		else: 
			self.output_file_ptr.seek(0)
			return False, None
	def get_final_frac_cosh(self):
		
		#
		# check if gulp run status: check_status()<list[2]> : updated by 'ExtractGULP.check_finish_normal()'
		#
		if False in self.check_status():
			return False, None
		
		pattern = False
		atomlist = []

		for line in self.output_file_ptr:
			if self.OutputConfig['FinalFrac']['pattern'] in line:
				pattern = True
				break
		
		if pattern:

			iterator = iter(self.output_file_ptr)

			#
			# skipping 'self.OutputConfig['FinalFrac']['space']' number of lines
			#
			for i in range(self.OutputConfig['FinalFrac']['space']):
				next(iterator)

			while True:

				strings = next(iterator).split()
				if len(strings) < 7:
				# e.g., string will be like '1  Tc    c     0.717584    0.345205    0.421269    0.000000' --> 7 letters
					break
				if strings[2] == 'c':		# if this is core
					atom = [ strings[1], 'core', float(strings[3]), float(strings[4]), float(strings[5]) ]
					atomlist.append(atom)
				if strings[2] == 's':
					atom = [ strings[1], 'shel', float(strings[3]), float(strings[4]), float(strings[5]) ]
					atomlist.append(atom)

			self.output_file_ptr.seek(0)
			return True, atomlist

		else: 
			self.output_file_ptr.seek(0)
			return False, None
	# --------------------------------------------------------------------------------------------------------------------
	def get_final_lvectors(self):

		if False in self.check_status():
			return False, None

		pattern = False
		lvectors = []

		for line in self.output_file_ptr:
			if self.OutputConfig['LattVectors']['pattern'] in line:
				pattern = True
				break

		if pattern:

			iterator = iter(self.output_file_ptr)
			next(iterator)

			lvectors.append(next(iterator).split())	
			lvectors.append(next(iterator).split())	
			lvectors.append(next(iterator).split())	

			for i in range(3):
				for j in range(3):
					lvectors[i][j] = float(lvectors[i][j])

			self.output_file_ptr.seek(0)
			return True, lvectors

		else:
			self.output_file_ptr.seek(0)
			return False, None

	# --------------------------------------------------------------------------------------------------------------------
	def get_final_lparams(self):

		if False in self.check_status():
			return False, None

		pattern = False
		lparams = []

		for line in self.output_file_ptr:
			if self.OutputConfig['LattParams']['pattern'] in line:
				pattern = True
				break

		if pattern:

			iterator = iter(self.output_file_ptr)
			next(iterator)
			next(iterator)
			lparams.append(float(next(iterator).split()[1]))
			lparams.append(float(next(iterator).split()[1]))
			lparams.append(float(next(iterator).split()[1]))
			lparams.append(float(next(iterator).split()[1]))
			lparams.append(float(next(iterator).split()[1]))
			lparams.append(float(next(iterator).split()[1]))

			self.output_file_ptr.seek(0)
			return True, lparams

		else:
			self.output_file_ptr.seek(0)
			return False, None

	# --------------------------------------------------------------------------------------------------------------------
	def get_final_lvolume(self):

		if False in self.check_status():
			return False, None

		for line in self.output_file_ptr:
			if self.OutputConfig['LattVol']['pattern'] in line:
				volume = float(line.strip().split()[self.OutputConfig['LattVol']['loc']-1])
				self.output_file_ptr.seek(0)
				return True, volume

		# end for
		self.output_file_ptr.seek(0)
		return False, None

	# --------------------------------------------------------------------------------------------------------------------
	def get_bulkmod(self):
	
		if False in self.check_status():
			return False, None

		modulus = []

		for line in self.output_file_ptr:
			if self.Property['BulkMod']['pattern'] in line:
				strings = line.strip().split()
				modulus = [ float(strings[4]), float(strings[5]), float(strings[6]) ]
				self.output_file_ptr.seek(0)
				return True, modulus
		# end for
		self.output_file_ptr.seek(0)
		return False, None
	# --------------------------------------------------------------------------------------------------------------------
	def get_youngsmod(self):

		if False in self.check_status():
			return False, None

		modulus = []

		for line in self.output_file_ptr:
			if self.Property['YoungsMod']['pattern'] in line:
				strings = line.strip().split()
				modulus = [ float(strings[4]), float(strings[5]), float(strings[6]) ]
				self.output_file_ptr.seek(0)
				return True, modulus
		# end for
		self.output_file_ptr.seek(0)
		return False, None
	# --------------------------------------------------------------------------------------------------------------------
	def get_compress(self):

		if False in self.check_status():
			return False, None

		compress = []

		for line in self.output_file_ptr:
			if self.Property['Compress']['pattern'] in line:
				compress = float(line.strip().split()[self.Property['Compress']['loc']-1])
				self.output_file_ptr.seek(0)
				return True, compress
		# end for
		self.output_file_ptr.seek(0)
		return False, None
	# --------------------------------------------------------------------------------------------------------------------
	def get_sdielec(self):

		if False in self.check_status():
			return False, None

		pattern = False
		dielec = []

		for line in self.output_file_ptr:
			if self.Property['StaticDielec']['pattern'] in line:
				pattern = True
				break

		if pattern:

			iterator = iter(self.output_file_ptr)
			next(iterator)
			next(iterator)
			next(iterator)
			next(iterator)

			#dielec.append(next(iterator).split()[1:])	
			#dielec.append(next(iterator).split()[1:])	
			#dielec.append(next(iterator).split()[1:])	

			l1 = next(iterator).strip()
			dx = []
			dx.append(l1[1:13].strip())
			dx.append(l1[13:23].strip())
			dx.append(l1[23:].strip())
			l1 = next(iterator).strip()
			dy = []
			dy.append(l1[1:13].strip())
			dy.append(l1[13:23].strip())
			dy.append(l1[23:].strip())
			l1 = next(iterator).strip()
			dz = []
			dz.append(l1[1:13].strip())
			dz.append(l1[13:23].strip())
			dz.append(l1[23:].strip())
		
			dielec.append(dx)
			dielec.append(dy)
			dielec.append(dz)

			for i in range(3):
				for j in range(3):
					try:
						dielec[i][j] = float(dielec[i][j])
					except ValueError:
						dielec[i][j] = 'NaN'
						self.output_file_ptr.seek(0)
						return False, None

			self.output_file_ptr.seek(0)

			# diagonalisation
			evals, evecs = np.linalg.eig(np.array(dielec))

			return True, [ dielec, evals.tolist() ]

		else:
			self.output_file_ptr.seek(0)
			return False, None
	# --------------------------------------------------------------------------------------------------------------------
	def get_hdielec(self):

		if False in self.check_status():
			return False, None

		pattern = False
		dielec = []

		for line in self.output_file_ptr:
			if self.Property['HighDielec']['pattern'] in line:
				pattern = True
				break

		if pattern:

			iterator = iter(self.output_file_ptr)
			next(iterator)
			next(iterator)
			next(iterator)
			next(iterator)

			#dielec.append(next(iterator).split()[1:])	
			#dielec.append(next(iterator).split()[1:])	
			#dielec.append(next(iterator).split()[1:])	

			l1 = next(iterator).strip()
			dx = []
			dx.append(l1[1:13].strip())
			dx.append(l1[13:23].strip())
			dx.append(l1[23:].strip())
			l1 = next(iterator).strip()
			dy = []
			dy.append(l1[1:13].strip())
			dy.append(l1[13:23].strip())
			dy.append(l1[23:].strip())
			l1 = next(iterator).strip()
			dz = []
			dz.append(l1[1:13].strip())
			dz.append(l1[13:23].strip())
			dz.append(l1[23:].strip())
		
			dielec.append(dx)
			dielec.append(dy)
			dielec.append(dz)

			for i in range(3):
				for j in range(3):
					try:
						dielec[i][j] = float(dielec[i][j])
					except ValueError:
						dielec[i][j] = 'NaN'
						self.output_file_ptr.seek(0)
						return False, None

			self.output_file_ptr.seek(0)

			# diagonalisation
			evals, evecs = np.linalg.eig(np.array(dielec))

			return True, [ dielec, evals.tolist() ]

		else:
			self.output_file_ptr.seek(0)
			return False, None
	# --------------------------------------------------------------------------------------------------------------------
	# --------------------------------------------------------------------------------------------------------------------
	# --------------------------------------------------------------------------------------------------------------------
	
'''
	unit test
'''
if __name__ == '__main__':

	gex = ExtractGULP()

	#fcheck = gex.set_output_file('/home/uccawkj/MultiToolkit/Extractor/A13.gout') 	# YOUNG
	fcheck = gex.set_output_file('/work/e05/e05/wkjee/Software/MultiToolkit/Extractor/demo_gulp_files/A13.gout')

	print(' ------ file 1')
	if fcheck:
		# checklist
		print('finish       :',gex.check_finish_normal())

		print('final energy :',gex.get_final_energy())
		print('final gnorm  :',gex.get_final_gnorm(gnorm_tol=1.E-6))
		#print('final gnorm  :',gex.get_final_gnorm())
	
		print('final frac   :',gex.get_final_frac())
		cslist = gex.get_final_frac_cosh()
		print(f' * FINAL FRAC')
		for atom in cslist[1]:
			print(atom)

		full_energy = gex.get_final_energy_full()
		for energy in full_energy:
			print(energy)

		init_energy = gex.get_initial_energy()
		print(init_energy)

		full_init_energy = gex.get_initial_energy_full()
		for energy in full_init_energy:
			print(energy)


		# get init frac
		print(f' * INITIAL FRAC')
		cslist_init = gex.get_initial_frac_cosh()
		for atom in cslist_init[1]:
			print(atom)

		print(f' * initial lattice vectors', gex.get_initial_lvectors())

		#print('final energy :',gex.get_final_energy())
		#print('final gnorm  :',gex.get_final_gnorm(gnorm_tol=1.E-6))

		print('final lvecs  :',gex.get_final_lvectors())
		print('final lparams:',gex.get_final_lparams())
		print('final volume :',gex.get_final_lvolume())

		print(' -- props')
		print('Bulk   Mod   :',gex.get_bulkmod())
		print('Youngs Mod   :',gex.get_youngsmod())
		print('Compress     :',gex.get_compress())
		print('StaticDielec :',gex.get_sdielec())
		print('HighFqDielec :',gex.get_hdielec())

		gex.reset()

	#fcheck = gex.set_output_file('/home/uccawkj/MultiToolkit/Extractor/demo_gulp_files/gulp.got')
	fcheck = gex.set_output_file('/work/e05/e05/wkjee/Software/MultiToolkit/Extractor/demo_gulp_files/gulp.got')

	print(' ------ file 2')
	if fcheck:
		# checklist
		print('finish       :',gex.check_finish_normal())

		print('final energy :',gex.get_final_energy())
		print('final gnorm  :',gex.get_final_gnorm(gnorm_tol=1.E-6))
		#print('final gnorm  :',gex.get_final_gnorm())
	
		print('final frac   :',gex.get_final_frac())
		#print('final energy :',gex.get_final_energy())
		#print('final gnorm  :',gex.get_final_gnorm(gnorm_tol=1.E-6))

		print('final lvecs  :',gex.get_final_lvectors())
		print('final lparams:',gex.get_final_lparams())
		print('final volume :',gex.get_final_lvolume())

		print(' -- props')
		print('Bulk   Mod   :',gex.get_bulkmod())
		print('Youngs Mod   :',gex.get_youngsmod())
		print('Compress     :',gex.get_compress())
		print('StaticDielec :',gex.get_sdielec())
		print('HighFqDielec :',gex.get_hdielec())

		gex.reset()

	#print(gex.set_output_file('bac'))
	#print(gex.check_finish_normal())
	#print(gex.check_gnorm_normal(gnorm_tol=1.E-6))

	cell = Cell()
	#print(gp.InputConfig['IrAtomsShells']['loc'])
	#print(gp.InputConfig['IrAtomsShells']['pattern'])

