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

	def __init__(self):

		self.atom_list = []

	'''
		setters
	'''
	def add_atom(self,atom):
		self.atom_list.append(atom)

	def create_atom(self,element,cart,cart2=None):

		if cart2 is None:
			atom = Atom()
			atom.set_atom0d(element,cart)
			self.atom_list.append(atom)

		if cart2 is not None:
			atom = Shell()
			atom.set_atom0d(element,cart,cart2)
			self.atom_list.append(atom)

	def set_atom_list(self,atom_list):
		
		self.atom_list = atom_list

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

	def empty_cluster(self):
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
	def print_cart_gulp(self,show_shel=True):

		#
		# show_shel : usage : False : keep shel species -> but put it's core as 'shel' to keep using shell model
		#
		for atom in self.atom_list:
			if atom.get_attr_gulp() == 'atom':
				atom.print_cart_gulp()
			if atom.get_attr_gulp() == 'shel':
				atom.print_cart_gulp(show_shel=show_shel)

	def print_cart_fhiaims(self):
		for atom in self.atom_list:
			atom.print_cart_fhiaims()

	# Non Standard
	def print_cart(self):
		for atom in self.atom_list:
			atom.print_cart()

	'''
		file write
	'''
	def write_config_gulp(self,path=None,name='config.gulp',show_shel=True):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			print('cartesian')
			self.print_cart_gulp(show_shel=show_shel)
		captured_stdout = stdout_buffer.getvalue()

		try:
			with open(name,'w') as f:
				f.write(captured_stdout)
				f.flush()
		except FileNotFoundError as e:
			print(e)

	def write_config_fhiaims(self,path=None,name='config.fhiaims'):

		if path is not None:
			if os.path.exists(path):	# if path true
				path = os.path.join(path,name)
				name = path
			#else -> in-place writing
		stdout_buffer = io.StringIO()
		with contextlib.redirect_stdout(stdout_buffer):
			self.print_cart_fhiaims()
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
	#shel.set_atom3d('O',[[4,0.5,0],[0,4,0],[0,0,5]],[0.5,0.5,0])

	atom.print_cart()
	shel.print_cart()

	atom.print_frac()
	shel.print_frac()

	print(' --')
	atom.print_cart_fhiaims()
	shel.print_cart_fhiaims()
	print(' --')
	atom.print_frac_fhiaims()
	shel.print_frac_fhiaims()

	print(' -- cluster')
	cluster = Cluster()
	cluster.add_atom(atom)
	cluster.add_atom(shel)
	
	cluster.print_cart_gulp()
	print(' --')
	cluster.print_cart()
	print(cluster.get_number_of_atoms())
	print(' --')
	cluster.print_cart_gulp(show_shel=False)
	print(' --')
	cluster.print_cart_gulp(show_shel=False)
	
	# 19.09.2023 check
	# def write_config_gulp(self,path=None,name='config.gulp',show_shel=True):
	cluster.write_config_gulp(path='./run',name='1.luster.gulp')
	cluster.write_config_gulp(path='./run',name='2.luster.gulp',show_shel=False)
	
	cluster.write_config_fhiaims(path='./run',name='1.luster.fhiaims')

	
