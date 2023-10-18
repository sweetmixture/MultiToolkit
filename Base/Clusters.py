#!/bin/python

'''
    Author  :   wkjee
    Title   :   OutputParser

    Layout

    /root
        /Base
			Atoms.py    : Atom, Shell
		  *	Clusters.py : Cluster
			Cells.py    : Cell
    
    18.09.2023  : framework
'''
import numpy as np
import os,sys,io
import contextlib

from Base.Atoms import Atom, Shell

class Cluster(object):

	def __init__(self,name=None):

		self.name = name
		self.atom_list = []

	'''
		setters
	'''
	def add_atom(self,atom):
		self.atom_list.append(atom)

	def set_atom_list(self,atom_list):
		self.atom_list = atom_list

	def create_atom(self,element,cart,cart_shel=None):

		if cart_shel is None:
			atom = Atom()
			atom.set_atom0d(element,cart)
			self.atom_list.append(atom)

		if cart_shel is not None:
			atom = Shell()
			atom.set_atom0d(element,cart,cart_shel)
			self.atom_list.append(atom)
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

	'''
		Utils
	'''
	# delemte atoms too close to each other
	def remove_duplicates(self,cutd=0.05):

		NotImplemented

	'''
		print message
	'''
	def print_atoms(self,mode=None,shel=False): # internal use

		for atom in self.atom_list:
			atom.print_atom(mode=mode,shel=shel)

	'''
		file write
	'''
	def write_gulp(self,path=None,name='cluster.gulp',shel=False,stdout=False):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
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

	def write_fhiaims(self,path=None,name='cluster.fhiaims',stdout=False):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
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

	def write_xyz(self,path=None,name='cluster.xyz'):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			print(f' {self.get_number_of_atoms()}')
			print('')
			self.print_atoms(mode='xyz')
		captured_stdout = stdout_buffer.getvalue()

		try:
			with open(name,'w') as f:
				f.write(captured_stdout)
				f.flush()
		except FileNotFoundError as e:
			print(e)

if __name__ == "__main__":

	atom = Atom()
	atom.set_atom3d('Mg',[[4,0.5,0],[0,4,0],[0,0,5]],[0.25,0.25,0.75])
	shel = Shell()
	shel.set_atom3d('O',[[4,0.5,0],[0,4,0],[0,0,5]],[0.5,0.5,0],[0.498,0.5131,-0.00313])

	atom.print_atom(mode='cart_fhiaims')
	atom.print_atom(mode='frac_fhiaims')
	shel.print_atom(mode='cart_fhiaims')
	shel.print_atom(mode='frac_fhiaims')

	atom.print_atom(mode='cart_gulp',shel=False)
	atom.print_atom(mode='frac_gulp',shel=False)
	shel.print_atom(mode='cart_gulp',shel=False)
	shel.print_atom(mode='frac_gulp',shel=False)

	print('-- cluster')
	cluster = Cluster()
	cluster.add_atom(atom)
	cluster.add_atom(shel)
	
	cluster.print_atoms(mode='xyz',shel=False)
	cluster.print_atoms(mode='cart_gulp',shel=False)
	cluster.print_atoms(mode='cart_gulp',shel=True)
	cluster.print_atoms(mode='frac_gulp',shel=False)
	cluster.print_atoms(mode='frac_gulp',shel=True)
	cluster.print_atoms(mode='cart_fhiaims')
	cluster.print_atoms(mode='frac_fhiaims')

	print('--write gulp')
	cluster.write_gulp()
	cluster.write_gulp(path='./run',name='gulp_shel.gin',shel=True)
	cluster.write_gulp(path='./run',name='gulp.gin')
	print('--write fhiaims')
	cluster.write_fhiaims()
	cluster.write_fhiaims(path='./run',name='fhiaims.in')
	print('--write xyz')
	cluster.write_xyz()
	cluster.write_xyz(path='./run',name='cluster.xyz')

	sys.exit()
