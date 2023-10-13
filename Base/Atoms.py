#!/bin/python
'''
	Author	:	wkjee
	Title	:	OutputParser

	Layout

	/root
		/Base
		  *	Atoms.py	: Atom, Shell
			Clusters.py	: Cluster
			Cells.py	: Cell

	18.09.2023	: framework
'''
import numpy as np
import sys

class Atom(object):

	def __init__(self,element=None):

		# element name : e.g., C, N, O ...
		self.element = element

		self.cart = [ None for i in range(3) ]		# Cartesian
		self.frac = [ None for i in range(3) ]		# Fractional

		self.lvectors = [ [ None for i in range(3) ] for j in range(3) ]		# Lattice vectors

	'''
		basic setters
	'''
	def set_element(self,element):	# element -> <str>
		self.element = element

	def set_cart(self,cart):		# cart -> list(3) : <float> * 3	: !!! could be <str> number
		if len(cart) == 3:
			for i in range(3):
				try:
					cart[i] = float(cart[i])
					self.cart[i] = cart[i]
				except:
					print(f'Err casting float() cart failed',file=sys.stderr)
					print(f'Err src : {__file__}',file=sys.stderr)
					sys.exit()
		else:
			print(f'Err cart dimension is not 3',file=sys.stderr)
			print(f'Err src : {__file__}',file=sys.stderr)
			sys.exit()

	def set_frac(self,frac):		# frac -> list(3) : <float> * 3 : !!! could be <str> number
		if len(frac) == 3:
			for i in range(3):
				try:
					frac[i] = float(frac[i])
					self.frac[i] = frac[i]
				except:
					print(f'Err casting float() frac faield',file=sys.stderr)
					print(f'Err src : {__file__}',file=sys.stderr)
					sys.exit()
		else:
			print(f'Err frac dimension is not 3',file=sys.stdrr)
			print(f'Err src : {__file__}',file=sys.stderr)
			sys.exit()

	def set_lvectors(self,lvectors): # lvectors -> list(3,3) : <float> 3*3 : !!! could be <str> number

		if len(lvectors) == 3 and len(lvectors[0]) == 3:

			for i in range(3):
				for j in range(3):
					try:
						lvectors[i][j] = float(lvectors[i][j])
					except:
						print(f'Err casting float() lvectors failed',file=sys.stderr)
						print(f'Err src : {__file__}',file=sys.stderr)
						sys.exit()

			self.lvectors = lvectors
		else:
			print(f'Err lvector dimension is not 3 x 3',file=sys.stderr)
			print(f'Err src : {__file__}',file=sys.stderr)
			sys.exit()

	'''
		internal uses
	'''
	def frac2cart(self):
		# fractional to cartesian conversion
		# req : lvectors,frac
		np_frac = np.array(self.frac)
		np_lv   = np.array(self.lvectors)
		self.cart = np.dot(np_lv.T,np_frac).tolist()
	
	def cart2frac(self):
		# fractional to cartesian conversion
		# req : lvectors,cart
		np_cart = np.array(self.cart)
		np_lvT = np.array(self.lvectors).T
		np_lvT_inv = np.linalg.inv(np_lvT)
		self.frac = np.dot(np_lvT_inv,np_cart).tolist()

	'''
		derived setters
	'''
	def set_atom0d(self,element,cart):
		'''
			Dimension 0 -> Cluster : req 'element', 'cart'
		'''
		self.set_element(element)
		self.set_cart(cart)

	def set_atom3d(self,element,lvectors,cd,mode='frac'):
		'''
			Dimension 3 -> 3D Periodic : req 'element', 'lvectors', 'frac'
			'cd' : coordinate <list:float>[3] : either fractional / cartesian
		'''
		self.set_element(element)
		self.set_lvectors(lvectors)

		if mode == 'frac':
			self.set_frac(cd)
			self.frac2cart()			# save 'cart' from 'frac'
		elif mode == 'cart':
			self.set_cart(cd)
			self.cart2frac()			# save 'frac' from 'cart'
		else:
			print(f"Err input mode must be either 'frac' or 'cart'",file=sys.stderr)
			print(f'Err src : {__file__}',file=sys.stderr)
			sys.exit()
			

	'''
		getters (including returns)
	'''
	def get_element(self):
		return self.element
	
	def get_cart(self):
		return self.cart

	def get_frac(self):
		return self.frac

	def get_attr_gulp(self):
		return 'core'

	'''
		print messages
	'''
	def print_atom(self,mode=None):

		if mode == 'xyz':
			print("%4s%14.8f%14.8f%14.8f" % (self.element,self.cart[0],self.cart[1],self.cart[2]))
		elif mode == 'cart_gulp':
			print("%4s%6s%14.8f%14.8f%14.8f" % (self.element,'core',self.cart[0],self.cart[1],self.cart[2]))
		elif mode == 'frac_gulp':
			print("%4s%6s%14.8f%14.8f%14.8f" % (self.element,'core',self.frac[0],self.frac[1],self.frac[2]))
		elif mode == 'cart_fhiaims':
			print("%4s%14.8f%14.8f%14.8f%4s" % ('atom',self.cart[0],self.cart[1],self.cart[2],self.element))
		elif mode == 'frac_fhiaims':
			print("%4s%14.8f%14.8f%14.8f%4s" % ('atom',self.frac[0],self.frac[1],self.frac[2],self.element))
		else:
			print(f'Err print_atom() mode is not set : possible modes : xyz, cart_gulp, frac_gulp, cart_fhiaims, frac_fhiaims',file=sys.stderr)
			print(f'Err src: {__file__}',file=sys.stderr)
			sys.exit()

	# ------- deprecated 
	def print_xyz(self):
		print("%4s%14.8f%14.8f%14.8f" % (self.element,self.cart[0],self.cart[1],self.cart[2]))

	def print_cart_gulp(self):
		print("%4s%6s%14.8f%14.8f%14.8f" % (self.element,'core',self.cart[0],self.cart[1],self.cart[2]))
			
	def print_frac_gulp(self):
		print("%4s%6s%14.8f%14.8f%14.8f" % (self.element,'core',self.frac[0],self.frac[1],self.frac[2]))

	def print_cart_fhiaims(self):
		print("%4s%14.8f%14.8f%14.8f%4s" % ('atom',self.cart[0],self.cart[1],self.cart[2],self.element))

	def print_frac_fhiaims(self):
		print("%9s%14.8f%14.8f%14.8f%4s" % ('atom_frac',self.frac[0],self.frac[1],self.frac[2],self.element))

	# Non standards
	def print_cart(self):
		print("%3s%14.8f%14.8f%14.8f core" % (self.element,self.cart[0],self.cart[1],self.cart[2]))

	def print_frac(self):
		print("%3s%14.8f%14.8f%14.8f core" % (self.element,self.frac[0],self.frac[1],self.frac[2]))



class Shell(Atom):

	def __init__(self,element=None):

		super().__init__(element)
	
		self.cart_shel = [ None for i in range(3) ]      # Shell cartesian
		self.frac_shel = [ None for i in range(3) ]      # Shell fractional

	'''
		basic setters
	'''
	def set_cart_shel(self,cart):        # cart -> list(3) : <float> * 3
		self.cart_shel = [ float(cart[0]), float(cart[1]), float(cart[2]) ]

	def set_frac_shel(self,frac):        # frac -> list(3) : <float> * 3
		self.frac_shel = [ float(frac[0]), float(frac[1]), float(frac[2]) ]

	'''
    	internal uses
	'''
	def frac2cart_shel(self):
		np_lv   = np.array(self.lvectors)
		np_frac = np.array(self.frac_shel)
		self.cart_shel = np.dot(np_lv.T,np_frac).tolist()

	'''
		derived setters
	'''
	def set_atom0d(self,element,cart,cart_shel=None):
		super().set_atom0d(element,cart)
		if cart_shell == None:
			self.set_cart_shel(self.get_cart())
		else:
			self.set_cart_shel(cart_shel)	

	def set_atom3d(self,element,lvectors,frac,frac_shel=None):
		super().set_atom3d(element,lvectors,frac)
		if frac_shel == None:
			self.set_frac_shel(frac)
		else:
			self.set_frac_shel(frac_shel)
		self.frac2cart_shel()		# using lvectors + frac -> calculate cart

	'''
		getters (including returns)
	'''
	def get_cart_shel(self):
		return self.cart_shel

	def get_frac_shel(self):
		return self.frac_shel

	def get_attr_gulp(self):
		return 'shel'
	'''
		print messages
	'''
	def print_cart_gulp(self,show_shel=True):

		super().print_cart_gulp()
		if show_shel is True:
			print("%4s%6s%14.8f%14.8f%14.8f" % (self.element,'shel',self.cart_shel[0],self.cart_shel[1],self.cart_shel[2]))

	def print_frac_gulp(self,show_shel=True):
		
		super().print_frac_gulp()
		if show_shel is True:
			print("%4s%6s%14.8f%14.8f%14.8f" % (self.element,'shel',self.frac_shel[0],self.frac_shel[1],self.frac_shel[2]))

	# Non standards
	def print_cart(self):
		super().print_cart()
		print("%3s%14.8f%14.8f%14.8f shell" % (self.element,self.cart_shel[0],self.cart_shel[1],self.cart_shel[2]))

	def print_frac(self):
		super().print_cart()
		print("%3s%14.8f%14.8f%14.8f shell" % (self.element,self.frac_shel[0],self.frac_shel[1],self.frac_shel[2]))


if __name__ == "__main__":

	atom = Atom()
	atom.set_atom3d('Mg',[[4,0.5,0],[0,4,0],[0,0,5]],[0.25,0.25,0.75],mode='frac')
	
	#shel = Shell()
	#shel.set_atom3d('O',[[4,0.5,0],[0,4,0],[0,0,5]],[0.5,0.5,0],[0.498,0.5131,-0.00313])
	#shel.set_atom3d('O',[[4,0.5,0],[0,4,0],[0,0,5]],[0.5,0.5,0])

	atom.print_atom(mode='xyz')
	atom.print_atom(mode='frac_gulp')
	atom.print_atom(mode='cart_gulp')
	atom.print_atom(mode='frac_fhiaims')
	atom.print_atom(mode='cart_fhiaims')

	print(" --")

	# reusing test
	atom.set_atom3d('O',[[4,'0',0],[0,4,0],[0,0,5]],['2','2','2'],mode='cart')
	atom.print_atom(mode='xyz')
	atom.print_atom(mode='frac_gulp')
	atom.print_atom(mode='cart_gulp')
	atom.print_atom(mode='frac_fhiaims')
	atom.print_atom(mode='cart_fhiaims')

	print(" --")
	
	sys.exit()

	atom.print_cart()
	shel.print_cart()
	print(" --")
	atom.print_frac()
	shel.print_frac()
	print(" --")
	atom.print_cart_fhiaims()
	shel.print_cart_fhiaims()
	print(" --")
	atom.print_frac_fhiaims()
	shel.print_frac_fhiaims()
	print(" --")

	print(' ----')
	atom.print_cart_gulp()
	shel.print_cart_gulp()
	print(' ----')
	atom.print_cart_gulp()
	shel.print_cart_gulp(show_shel=False)
	print(' ----')

	# unittest
	#atom.set_atom3d('Mg',[0.5,0.5,0],[[4,0.5,0],[0,4,0],[0,0,5]])
	#atom.print_cart()
	#atom.print_cart_fhiaims()

	# unittest
	#atom.set_atom0d('O',[0.1,-0.2,3.])
	#atom.print_cart()
	#atom.print_cart_fhiaims()

	print(shel.get_attr_gulp())
	print(shel.get_cart())
	print(shel.get_cart_shel())
	print(shel.get_frac())
	print(shel.get_frac_shel())
