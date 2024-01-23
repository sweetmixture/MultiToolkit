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
            GULP.py     : GULP_Patterns, ExtractGULP
            FHIaims.py  : FHIaims_Patterns, ExtractFHIaims

          *  GULPstruct.py

    19.09.2023  : framework

    30.11.2023  : structure extractor back-bone

    03.12.2023  : RDF calculator -> using pymatgen / vasppy

'''

import os,sys
import numpy as np

from pymatgen.core import Lattice,Structure				# using 'pymatgen'
#from Extractor.GULP import GULP_Patterns
from Extractor.GULP import ExtractGULP
from vasppy.rdf import RadialDistributionFunction		# using 'vasppy'

''' function internal use only '''
#
# update required ... for normalisation later - 03.12.2023
#
def get_gaussian(A,r0,r,sigma):
	
	#A = np.float128(A)
	#r0= np.float128(r0)
	#r = np.float128(r)
	#sigma = np.float128(sigma)		
	return A * np.exp(-(r-r0)*(r-r0)/sigma/sigma)



'''
	(1) RDF generator
'''
class GULPLattice(ExtractGULP):

	def __init__(self):
		super().__init__()		# load GULP_Patterns

		# ---- overriding default parameters in 'ExtractGULP'	:	using filetype=None
		# note: class attributes names starting with '__' are not inherited to the child class (?)
		#
		self.__FileNormal = False
		self.__FinishNormal = False
		self.output_file = None
		self.output_file_ptr = None

		# PARAMETERS
		self.__gnorm_tol = 1.E-3    # 0.001

	def set_lattice(self,filepath,filetype=None):

		'''
			Method Description

			(1) read standard gulp output file ( NoSymmetry Lattice )

				* get lattice vectors / * lattice parameters / * factional coordinates of atoms

				>> saved into 'pymatgen' object Structure

			!
			! 22-01-2024
			! further developement - supporting reading in gulp 'gin' format / 'cif' format
			!
		'''

		if filetype is None:

			if self.set_output_file(filepath):
				if self.check_finish_normal():
					# methods from 'ExtractGULP'
					res1, lvectors = self.get_final_lvectors()
					res2, lparams  = self.get_final_lparams()
					res3, fatomlist= self.get_final_frac()

					if False not in [res1,res2,res3]:
						# Using 'pymatgen'
						# see docs: https://pymatgen.org/pymatgen.core.html#module-pymatgen.core.lattice
						#self.lattice = Lattice(lvectors)
						#print(self.lattice.abc) - lattice length check
		
						# extract species-list coord-list (fractional)
						specieslist = []
						coordlist = []
						for item in fatomlist:
							specieslist.append(item[0])
							coordlist.append(item[1:])
						# pymatgen object 'Structure'(lattice, nosymmetry)
						self.struct = Structure(lattice=lvectors,species=specieslist,coords=coordlist)

						#print('pymatgen lattice.abc:')
						#print(self.struct.lattice.abc)
						#print('pymatgen lattice.angles)
						#print(self.struct.lattice.angles)
						#print('pymatgent lattice')
						#print(self.struct)
						'''
							PossibleOutput
								Full Formula (Mg4 O4)
								Reduced Formula: MgO
								abc   :   3.877051   3.877051   3.877051
								angles:  90.000000  90.000000  90.000000
								pbc   :       True       True       True
								Sites (8)

								  #  SP      a    b    c
								---  ----  ---  ---  ---
								  0  Mg    0    0    0
								  1  Mg    0.5  0.5  0
								  2  Mg    0.5  0    0.5
								  3  Mg    0    0.5  0.5
								  4  O     0.5  0    1
								  5  O     0    0.5  0
								  6  O     0    1    0.5
								  7  O     0.5  0.5  0.5
						'''

					else:
						print(f'@Error> file:{self.output_file} cannot extract lattice information',file=sys.stderr)
						return
				else:
					print(f'@Warning> file:{self.output_file} gulp may finish abnormally',file=sys.stderr)		
			else:
				print(f'@Error> file:{self.output_file} does not exist',file=sys.stderr)		


		if filetype == 'gin':
			pass
		if filetype == 'cif':
			# possible reference for this implementation : see website tutorial:
			# https://workshop.materialsproject.org/lessons/02_intro_pymatgen/1%20-%20pymatgen%20foundations/#:~:text=Creating%20a%20Structure%20is%20very,have%20to%20specify%20a%20Lattice%20.&text=Creating%20this%20Structure%20was%20similar,and%20a%20list%20of%20positions.
			# BaTiO3=Structure.from_file("BaTiO3.cif")
			pass

	def get_rdf(self,pair=[None,None],gaussian=False,smearing=0.05,dist=10.0,stride=0.01,ifdummy=False):

		'''
			12/2023

			pair(<list[2]<str>>) str -> species name : e.g. ('Mg','O')

			gaussian : bool -> enable gaussian smearing or not
			smearing : only in effect if gaussian = True

			* Generating RDF information

		'''

		try:
			indices_A = [ i for i, site in enumerate(self.struct) if site.species_string == pair[0] ]
			indices_B = [ i for i, site in enumerate(self.struct) if site.species_string == pair[1] ]
			#print('ind A:', indices_A)
			#print('ind B:', indices_B)
		except Exception as e:
			print(f'@Error> in get_rdf(), getting species indices failed -> spcies1: {pair[0]}, species2: {pair[1]}',file=sys.stderr)
			return False, None

		if len(indices_A) == 0 or len(indices_B) == 0:
			#
			# no such species -> return dummy : vasppy generated-like empty rdf
			#

			if gaussian == True:
				_data_points = int(dist/stride)

				gauss_rdf_r = [ float(i)*stride for i in range(_data_points) ]  # max distance 10 Angstrom - default 
				gauss_rdf   = [ 0. for i in range(_data_points) ]

				return gauss_rdf_r, gauss_rdf

			else:
				r_sta = 0.01
				r_stride = 0.02
				rlist = []
				rdflist = []

				r = r_sta
				while r < 10.0:
					rlist.append(r)
					rdflist.append(0.)
					r += r_stride

				return rlist,rdflist
		# 
		# Get RadialDistributionFunction -> using vasppy
		#
		if pair[0] == pair[1]:
			rdf = RadialDistributionFunction(structures=[self.struct],indices_i=indices_A)
		else:
			rdf = RadialDistributionFunction(structures=[self.struct],indices_i=indices_A,indices_j=indices_B)
			
		#
		# Using Gaussian smearing ... default smearing factor '0.05': beware surrounding data around peaks will be contaminated
		#
		if gaussian == True:

			_data_points = int(dist/stride)

			gauss_rdf_r = [ float(i)*stride for i in range(_data_points) ] 	# max distance 10 Angstrom - default 
			gauss_rdf   = [ 0. for i in range(_data_points) ]

			for index,signal in enumerate(rdf.rdf):

				if signal > 0.:	# case if signal exists

					for gindex,gr in enumerate(gauss_rdf_r):

						ssignal = get_gaussian(signal,rdf.r[index],gr,smearing)

						if ssignal > 10E-12:
							gauss_rdf[gindex] = gauss_rdf[gindex] + ssignal
							
			return gauss_rdf_r, gauss_rdf	

		else:
			return rdf.r, rdf.rdf



if __name__=='__main__':

	_smearing = 0.05

	glattice = GULPLattice()
	glattice.set_lattice('/Users/woongkyujee/SkukuzaLocal/MultiToolkit/Extractor/gulp.got')	# upto here, setting pymatgen lattice : member_variable(propery) -> struct

	pair = ['Mg','Mg']
	r0, rdf0 = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)
	pair = ['Mg','O']
	r1, rdf1 = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)
	pair = ['O','O']
	r2, rdf2 = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)

	with open(f'MgO.rdf','w') as f:
		for i in range(len(r0)):
			f.write('%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n' % (r0[i],r1[i],r2[i],rdf0[i],rdf1[i],rdf2[i]))
			#                                                    r1    r2    r3    MgMg ,   MgO ,  OO

	glattice.reset()

	# rdf implementation reference : https://vasppy.readthedocs.io/en/latest/examples/rdfs.html

	# trial 2

	print('trial 2 ----- MnO2 -----')
	glattice.set_lattice('/Users/woongkyujee/SkukuzaLocal/MultiToolkit/Extractor/gulp_klmc.gout')
	#glattice.set_lattice('/Users/woongkyujee/SkukuzaLocal/MultiToolkit/Extractor/demo_gulp_files/A10753/gulp_klmc.gout')       #
	glattice.set_lattice('/Users/woongkyujee/SkukuzaLocal/MultiToolkit/Extractor/demo_gulp_files/n24gm.gout')                  #  Example : LiMnO2 R-phase
	#glattice.set_lattice('/Users/woongkyujee/SkukuzaLocal/MultiToolkit/Extractor/demo_gulp_files/A15664/gulp_klmc.gout')       #
	
	_smearing = 0.05

	pair = ['Tc','Tc']
	r0, rdf0 = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)
	pair = ['Li','Tc']
	r1, rdf1 = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)
	pair = ['Li','Li']
	r2, rdf2 = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing)

	glattice.reset()

	print(' ----- lengths ----- ')
	print(len(r0))
	print(len(r1))
	print(len(r2))

	with open(f'{sys.argv[1]}','w') as f:
		for i in range(len(r0)):
			f.write('%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n' % (r0[i],r1[i],r2[i],rdf0[i],rdf1[i],rdf2[i]))
			#                                                    r1    r2    r3    TcTc ,  TcLi ,  LiLi

	# demonstration done ... 03 DEC 2023
