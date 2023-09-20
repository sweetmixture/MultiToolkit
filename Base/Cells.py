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

	def __init__(self):

		self.lvectors = [[0. for i in range(3)] for i in range(3)]
		self.lconstants = [0. for i in range(3)]
		self.langles = [0. for i in range(3)]
		self.volume = 0.

		self.atom_list = []

	'''
		setters
	'''
	def set_lvectors(self,lvectors):
		self.lvectors = lvectors

	def set_lconstants(self,lconstants):
		self.lconstants = lconstants

	def set_langles(self,langles):
		self.langles = langles

	def set_volume(self):
		self.volume = np.abs(np.dot(np.array(self.lvectors[0]),np.cross(np.array(self.lvectors[1]),np.array(self.lvectors[2]))))

	def set_lattice(self,lvectors=None,lconstants=None,langles=None):

		#
		#	case : lvectors given 
		#
		#	[ ax, ay, az ]
		#	[ bx, by, bz ]
		#	[ cx, cy, cz ]	-> arbitrary orientation
		#
		if lvectors is not None and (lconstants is None and langles is None):

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

	def add_atom(self,atom,frac=None):
		self.atom_list.append(atom)

	def create_atom(self,element,frac,frac2=None):

		if frac2 is None:
			atom = Atom()
			atom.set_atom3d(element,self.lvectors,frac)
			self.atom_list.append(atom)

		if frac2 is not None:
			atom = Shell()
			atom.set_atom3d(element,self.lvectors,frac,frac2)
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
		'''

	'''
		destructors
	'''
	def del_atom(self,n):
		if n == -1:
			if len(self.atom_list) > 0:
				self.atom_list.pop()
		if 0 <= n < len(self.atom_list):
			del self.atom_list[n]
			self.atom_list = [ atom for atom in self.atom_list if atom is not None ]

	def empty_cell(self):
		self.atom_list.clear()

	'''
		getters
	'''
	def get_atom(self,n):
		if 0 <= n < len(self.atom_list):
			return self.atom_list[n]
		else:
			return None

	def get_number_of_atoms(self):
		return len(self.atom_list)

	'''
		print message
	'''
	# GULP input format comapatible
	def print_lvectors_gulp(self):
		print("vectors")
		for lvector in self.lvectors:
			print("%20.8f%14.8f%14.8f" % (lvector[0],lvector[1],lvector[2]))

	# FHIaims *.in format compatible
	def print_lvectors_fhiaims(self):
		for lvector in self.lvectors:
			print("lattice_vector %14.8f%14.8f%14.8f" % (lvector[0],lvector[1],lvector[2]))

	def print_cart_gulp(self,show_shel=True):

		for atom in self.atom_list:
			if atom.get_attr_gulp() == 'atom':
				atom.print_cart_gulp()
			if atom.get_attr_gulp() == 'shel':
				atom.print_cart_gulp(show_shel=show_shel)

	def print_frac_gulp(self,show_shel=True):

		for atom in self.atom_list:
			if atom.get_attr_gulp() == 'atom':
				atom.print_frac_gulp()
			if atom.get_attr_gulp() == 'shel':
				atom.print_frac_gulp(show_shel=show_shel)

	def print_cart_fhiaims(self):
		for atom in self.atom_list:
			atom.print_cart_fhiaims()

	def print_frac_fhiaims(self):
		for atom in self.atom_list:
			atom.print_frac_fhiaims()

	# Non standard
	def print_cart(self):
		for atom in self.atom_list:
			atom.print_cart()

	def print_frac(self):
		for atom in self.atom_list:
			atom.print_frac()
	
	'''
		file write
	'''
	def write_config_gulp(self,path=None,name='config.gulp',rule='frac',show_shel=True):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			self.print_lvectors_gulp()
			if rule == 'frac':
				print('fractional')
				self.print_frac_gulp(show_shel=show_shel)
			if rule == 'cart':
				print('cartesian')
				self.print_cart_gulp(show_shel=show_shel)
		captured_stdout = stdout_buffer.getvalue()

		try:
			with open(name,'w') as f:
				f.write(captured_stdout)
				f.flush()
		except FileNotFoundError as e:
			print(e)

	def write_config_fhiaims(self,path=None,name='config.fhiaims',rule='frac'):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			self.print_lvectors_fhiaims()
			if rule == 'frac':
				self.print_frac_fhiaims()
			if rule == 'cart':
				self.print_cart_fhiaims()
		captured_stdout = stdout_buffer.getvalue()

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

	cell3.print_lvectors_fhiaims()
	cell3.print_frac_fhiaims()

	cell3.print_lvectors_fhiaims()
	cell3.print_cart_fhiaims()
	
	print(' -- show all')
	cell3.print_cart_gulp()
	cell3.print_frac_gulp()

	print(' -- show')
	cell3.print_cart_gulp()
	cell3.print_frac_gulp()

	print(' -- show show_shel=False')
	cell3.print_cart_gulp(show_shel=False)
	cell3.print_frac_gulp(show_shel=False)

	print(' -- show show_shel=True') # implicitly True see Atoms.py
	cell3.print_cart_gulp()
	cell3.print_frac_gulp()

	# checked - 19.09.2023
	#cell3.write_config_gulp(path='./run',name='1.config.gulp',show_shel=False)
	#cell3.write_config_gulp(path='./run',name='2.config.gulp',show_shel=True)	# already implicity True 'show_shel'

	cell3.write_config_gulp(path='./run',name='3.config.gulp',rule='cart',show_shel=False)
	cell3.write_config_gulp(path='./run',name='4.config.gulp',rule='cart',show_shel=True)

	cell3.write_config_fhiaims(name='1.config.fhiaims',rule='cart')
	cell3.write_config_fhiaims(name='2.config.fhiaims',rule='frac')

	print(cell3.volume)
