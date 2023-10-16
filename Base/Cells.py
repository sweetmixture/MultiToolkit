#!/bin/python

'''
    Author  :   wkjee
    Title   :   OutputParser

    Layout

    /root
        /Base
			Atoms.py	: Atom, Shell
			Clusters.py	: Cluster
          * Cells.py	: Cell
    
    18.09.2023  : framework
'''

import numpy as np
import os,sys,io
import contextlib

from Base.Atoms import Atom, Shell

class Cell(object):

	def __init__(self,name=None):

		self.name		= name
		self.lvectors	= [ [0. for i in range(3)] for i in range(3)]
		self.lconstants = [ 0. for i in range(3)]
		self.langles	= [ 0. for i in range(3)]
		self.volume		= 0.
		self.atom_list	= []

	'''
		setters
	'''
	def set_lvectors(self,lvectors):
		if len(lvectors) == 3 and len(lvectors[0]) == 3:
			for i in range(3):
				for j in range(3):
					try:
						self.lvectors[i][j] = float(lvectors[i][j])
					except:
						print(f'Err casting float() lvectors failed',file=sys.stderr)
						print(f'Err src : {__file__}',file=sys.stderr)
						sys.exit()
		else:
			print(f'Err lvector dimension is not 3 x 3',file=sys.stderr)
			print(f'Err src : {__file__}',file=sys.stderr)
			sys.exit()

	def set_lconstants(self,lconstants):
		if len(lconstants) == 3:
			for i in range(3):
				try:
					self.lconstants[i] = float(lconstants[i])
				except:
					print(f'Err casting float() cart failed',file=sys.stderr)
					print(f'Err src : {__file__}',file=sys.stderr)
					sys.exit()
		else:
			print(f'Err lcontant dimension is not 3',file=sys.stderr)
			print(f'Err src : {__file__}',file=sys.stderr)
			sys.exit()

	def set_langles(self,langles):
		if len(langles) == 3:
			for i in range(3):
				try:
					self.langles[i] = float(langles[i])
				except:
					print(f'Err casting float() cart failed',file=sys.stderr)
					print(f'Err src : {__file__}',file=sys.stderr)
					sys.exit()
		else:
			print(f'Err langle dimension is not 3',file=sys.stderr)
			print(f'Err src : {__file__}',file=sys.stderr)
			sys.exit()

	def set_volume(self):
		self.volume = np.abs(np.dot(np.array(self.lvectors[0]),np.cross(np.array(self.lvectors[1]),np.array(self.lvectors[2]))))

	'''
		derived setter : 10.2023
	'''
	def set_lattice(self,lvectors=None,lconstants=None,langles=None):

		#
		#	case : lvectors given 
		#
		#	[ ax, ay, az ]
		#	[ bx, by, bz ]
		#	[ cx, cy, cz ]	-> arbitrary orientation
		#
		if lvectors is not None:

			self.set_lvectors(lvectors)
			self.set_volume()

			self.lconstants[0] = np.linalg.norm(np.array(self.lvectors[0]))
			self.lconstants[1] = np.linalg.norm(np.array(self.lvectors[1]))
			self.lconstants[2] = np.linalg.norm(np.array(self.lvectors[2]))
	
			self.langles[0] = np.rad2deg(np.arccos(np.dot(lvectors[1],lvectors[2])/np.linalg.norm(lvectors[1])/np.linalg.norm(lvectors[2])))
			self.langles[1] = np.rad2deg(np.arccos(np.dot(lvectors[0],lvectors[2])/np.linalg.norm(lvectors[0])/np.linalg.norm(lvectors[2])))
			self.langles[2] = np.rad2deg(np.arccos(np.dot(lvectors[0],lvectors[1])/np.linalg.norm(lvectors[0])/np.linalg.norm(lvectors[1])))
		#
		#	case : lconstants / lagles given
		#
		if lvectors is None and (lconstants is not None and langles is not None):

			self.set_lconstants(lconstants)
			self.set_langles(langles)

			a = [ lconstants[0], 0., 0. ]
			b = [ lconstants[1]*np.cos(np.deg2rad(langles[2])), lconstants[1]*np.sin(np.deg2rad(langles[2])), 0. ]
			c = [ lconstants[2]*np.cos(np.deg2rad(langles[1])), \
				  lconstants[2]*(np.cos(np.deg2rad(langles[0]))-np.cos(np.deg2rad(langles[1]))*np.cos(np.deg2rad(langles[2])))/np.sin(np.deg2rad(langles[2])), \
				  lconstants[2]*np.sqrt(1.-np.power(np.cos(np.deg2rad(langles[1])),2.)-np.power((np.cos(np.deg2rad(langles[0]))-np.cos(np.deg2rad(langles[1]))*np.cos(np.deg2rad(langles[2])))/np.sin(np.deg2rad(langles[2])),2.))]
		
			self.lvectors = [a,b,c]
			self.set_volume()

	def add_atom(self,atom):
		self.atom_list.append(atom)

	def create_atom(self,element,frac,frac_shel=None):

		if frac_shel is None:
			atom = Atom()
			atom.set_atom3d(element,self.lvectors,frac)
			self.atom_list.append(atom)

		if frac_shel is not None:
			atom = Shell()
			atom.set_atom3d(element,self.lvectors,frac,frac_shel)
			self.atom_list.append(atom)
	'''
		use in-place
	'''
	def set_std_orient(self):

		NotImplemented
		''' 
			algorithm
			step 1. get lconstants / langles : a b c / al be ga
			step 2. use conventional expression to re-define lattice vectors

			-> must use 'ASE' 
		'''

	'''
		destructors
	'''
	def del_atom(self,n):
		if n == -1:
			try:
				self.atom_list.pop()
			except:
				pass
		if 0 <= n < len(self.atom_list):
			del self.atom_list[n]
			self.atom_list = [ atom for atom in self.atom_list if atom is not None ]

	def empty(self):
		self.atom_list.clear()

	'''
		getters
	'''
	def get_atoms(self):
		return self.atom_list

	def get_atom(self,n):
		if 0 <= n < len(self.atom_list):
			return self.atom_list[n]
		else:
			return None

	def get_number_of_atoms(self):
		return len(self.atom_list)

	def get_lvectors(self):
		return self.lvectors

	def get_lattice_matrix(self):
		return np.array(self.get_lvectors()).transpose().tolist()

	def get_lconstants(self):
		return self.lconstants

	def get_langles(self):
		return self.langles

	def get_lvolume(self):
		return self.volume


	'''
		print message
	'''
	# GULP input format comapatible : internal use only
	def print_lvectors_gulp(self,vector=False):
		if vector is True:
			print('vectors')
			for lvector in self.lvectors:
				print('%14.8f%14.8f%14.8f' % (lvector[0],lvector[1],lvector[2]))
		elif vector is False:
			print('cell')
			print('%14.8f%14.8f%14.8f%14.8f%14.8f%14.8f' % (				\
				self.lconstants[0],self.lconstants[1],self.lconstants[2],		\
				self.langles[0],self.langles[1],self.langles[2]))

	# FHIaims *.in format compatible : internal use only
	def print_lvectors_fhiaims(self):
		for lvector in self.lvectors:
			print("lattice_vector %14.8f%14.8f%14.8f" % (lvector[0],lvector[1],lvector[2]))

	def print_atoms(self,mode=None,shel=False):
		for atom in self.atom_list:
			atom.print_atom(mode=mode,shel=shel)
	'''
		file write
	'''
	def write_gulp(self,path=None,name='cell.gulp',vector=False,rule='frac',shel=False,stdout=False):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			self.print_lvectors_gulp(vector=vector)
			if rule == 'frac':
				print('fractional')
				self.print_atoms(mode='frac_gulp',shel=shel)
			if rule == 'cart':
				print('cartesian')
				self.print_atoms(mode='cart_gulp',shel=shel)

		captured_stdout = stdout_buffer.getvalue()
	
		if stdout is True:
			print(captured_stdout)
			return

		try:
			with open(name,'w') as f:
				f.write(captured_stdout)
				f.flush()
		except FileNotFoundError as e:
			print(e)

	def write_fhiaims(self,path=None,name='cell.fhiaims',rule='frac',stdout=False):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			self.print_lvectors_fhiaims()
			if rule == 'frac':
				self.print_atoms(mode='frac_fhiaims')
			if rule == 'cart':
				self.print_atoms(mode='cart_fhiaims')
		captured_stdout = stdout_buffer.getvalue()

		if stdout is True:
			print(captured_stdout)
			return

		try:
			with open(name,'w') as f:
				f.write(captured_stdout)
				f.flush()
		except FileNotFoundError as e:
			print(e)

	def write_xyz(self,path=None,name='cell.xyz',stdout=False):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			print(f'{self.get_number_of_atoms()}')
			print('')
			self.print_atoms(mode='xyz')
		captured_stdout = stdout_buffer.getvalue()

		if stdout is True:
			print(captured_stdout)
			return

		try:
			with open(name,'w') as f:
				f.write(captured_stdout)
				f.flush()
		except FileNotFoundError as e:
			print(e)


if __name__ == "__main__":


	'''
		19.09.23 unittest
	'''
	cell = Cell()

	lvectors = [[8.887711,0.011848,0.000000],
				[0.012595,9.537254,0.000000],
				[0.000000,0.000000,8.573353]]

	cell2 = Cell()

	lconstants = [8.887719,9.537262,8.573353]
	langles    = [90.000000,90.000000,89.847953]


	cell.set_lattice(lvectors=lvectors)
	'''
		[8.887711, 0.011848, 0.0],
		[0.012595, 9.537254, 0.0],
		[0.0, 0.0, 8.573353]

		[8.88771889714256, 9.537262316542469, 8.573353]
		[90.0, 90.0, 89.84795500205209]
	'''
	cell2.set_lattice(lconstants=lconstants,langles=langles)


	cell3 = Cell()
	lvectors = [[4.2112,0.,0.],[0.,4.2112,0.],[0.,0.,5.312]]
	cell3.set_lattice(lvectors=lvectors)
	cell3.create_atom('Mg',[0.0,0.0,0.0])
	cell3.create_atom('Mg',[0.5,0.5,0.0])
	cell3.create_atom('Mg',[0.5,0.0,0.5])
	cell3.create_atom('Mg',[0.0,0.5,0.5])

	cell3.create_atom('O',[0.5,0.0,0.0],[0.5,0.0,0.0])	# create_atom shel
	cell3.create_atom('O',[0.0,0.5,0.0],[0.0,0.5,0.0])	# create_atom shel
	cell3.create_atom('O',[0.0,0.0,0.5],[0.0,0.0,0.5])	# create_atom shel
	cell3.create_atom('O',[0.5,0.5,0.5],[0.5,0.5,0.5])	# create_atom shel


	print('----possible combo 1')
	cell3.write_gulp(name='gcell_0')
	cell3.write_gulp(path='./run',name='gcell_1')
	cell3.write_gulp(path='./run',name='gcell_2',vector=True)
	cell3.write_gulp(path='./run',name='gcell_3',vector=True,rule='cart')
	cell3.write_gulp(path='./run',name='gcell_4',vector=True,rule='frac')
	cell3.write_gulp(path='./run',name='gcell_5',vector=True,rule='cart',shel=True)

	print('----possible combo 2')
	cell3.write_fhiaims(name='fcell_0')
	cell3.write_fhiaims(path='./run',name='fcell_1',rule='frac')
	cell3.write_fhiaims(path='./run',name='fcell_2',rule='cart')

	print('----possible combo 3')
	cell3.write_fhiaims(name='fcell_out',rule='cart',stdout=True)
	cell3.write_xyz(name='xyz_0',stdout=True)
	sys.exit()
