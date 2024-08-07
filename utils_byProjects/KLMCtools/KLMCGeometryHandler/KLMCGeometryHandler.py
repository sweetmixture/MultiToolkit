#
# 07.2024 W.JEE
#
# Read-in Standard Geometry Reader: 'xyz', 'cif', 'in' (not implemented)
#

from ase.io import read
import sys,os

class KLMCGeometryHandler:

	def __init__(self,filename=None):

		self._filename = filename
		self._struct = None
		self._cell   = None

		self.lattice_vectors = None
		self.lattice_parameters = None
		self.lattice_angles = None

		if filename is not None:
			try:
				self._struct = read(self._filename)
				self._cell   = self._struct.cell if self._struct.cell.any() else None
			except:
				self._struct = None
				self._cell   = None
				print(f'KLMCGeometryHandler: reading in geometry file failed ...')
				sys.exit(1)

			if self._cell is not None:

				self.lattice_vectors = self._cell.tolist()
				self.lattice_parameters = self._cell.lengths()
				self.lattice_angles = self._cell.angles()
		'''
			if periodic system

			self._struct
			self._cell
			self.lattice_vectors
			self.lattice_parameters
			self.lattice_angles

			else (non-periodic)
			
			self._struct
		'''
	def get_frac(self): # if non-periodic -> output: same with get_cart()
		frac = self._struct.get_scaled_positions()
		elem = self._struct.get_chemical_symbols()
		return elem, frac # 2d arr

	def get_cart(self):
		cart = self._struct.get_positions()
		elem = self._struct.get_chemical_symbols()
		return elem, cart # 2d arr

	#
	# GULP
	# 
	
	# * write GULP input file
	def write_gulp_input(self,keywords='', optionfile='option.file', fileout='klmc_gulp.gin'): 
						#	  ^^^^^^^^ str ^^^^^^^^^^ filepath       ^^^^^^^ output file name (GULPinput file name)
		#
		# get GULP options
		#
		options = None
		with open(optionfile,'r') as optfile:
			options = optfile.read()
		#
		# get geometry
		#
		elem, cart = self.get_cart()

		#
		# write fileout
		#
		with open(fileout,'w') as fout:

			fout.write(f'# Generated by KLMC converter\n')
			fout.write(f'# Input Source: {self._filename}\n')
			fout.write(f'{keywords}\n')
			#
			# periodic case
			#
			if self._cell is not None:
				fout.write('vectors\n')
				for lvec in self.lattice_vectors:
					fout.write(f'{lvec[0]:24.12f}{lvec[1]:24.12f}{lvec[2]:24.12f}\n')
				fout.write('cartesian\n')
				for species, cart in zip(elem,cart):
					fout.write(f'{species:4.3s}{cart[0]:24.12f}{cart[1]:24.12f}{cart[2]:24.12f}\n')
			#
			# non-periodic case
			#
			if self._cell is None:
				fout.write('cartesian\n')
				for species, cart in zip(elem,cart):
					fout.write(f'{species:4.3s}{cart[0]:24.12f}{cart[1]:24.12f}{cart[2]:24.12f}\n')
			# * add footer
			fout.write(options)

if __name__ == '__main__':

	print('\n* readin test')
	file = 'NaCl.cif'
	cell = KLMCGeometryHandler(file)
	print(cell.get_frac()) # 2d array
	print(cell.get_cart()) # 2d array

	print('\n* readin test')
	file = 'water.xyz'
	cell = KLMCGeometryHandler(file)
	print(cell.get_frac()) # 2d array
	print(cell.get_cart()) # 2d array

	print('\n* readin test')
	file = 'aims_perovskite.in'
	cell = KLMCGeometryHandler(file)
	print(cell.get_frac()) # 2d array
	print(cell.get_cart()) # 2d array

	print('\n* readin test')
	file = 'aims_Au25.in'
	cell = KLMCGeometryHandler(file)
	print(cell.get_frac()) # 2d array
	print(cell.get_cart()) # 2d array

	print(' ------------------------------\n')

	file = 'qubo_test.cif'
	cell = KLMCGeometryHandler(file)
	elem, cart = cell.get_frac()
	for species, pos in zip(elem,cart):
		print(species,pos)
	print(' * gulp write test')
	keywords = 'opti conp property full nosymm phon comp'
	cell.write_gulp_input(keywords=keywords,optionfile='gulp_NFP_footer')

	#
	# for Non-periodic
	#
	#file = 'water.xyz'
	#cell = KLMCGeometryHandler(file)
	#elem, cart = cell.get_frac()
	#for species, pos in zip(elem,cart):
	#	print(species,pos)
	#print(' * gulp write test')
	#keywords = 'opti conp property full nosymm phon comp'
	#cell.write_gulp_input(keywords=keywords,optionfile='gulp_NFP_footer')

