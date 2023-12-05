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

from pymatgen.core import Lattice,Structure
#from Extractor.GULP import GULP_Patterns
from Extractor.GULP import ExtractGULP
from vasppy.rdf import RadialDistributionFunction

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


class GULPLattice(ExtractGULP):

	def __init__(self):
		super().__init__()		# load GULP_Patterns

		# ---- overriding default parameters in 'ExtractGULP'	:	using filetype=None
		self.__FileNormal = False
		self.__FinishNormal = False
		self.output_file = None
		self.output_file_ptr = None

		# PARAMETERS
		self.__gnorm_tol = 1.E-3    # 0.001

	def set_lattice(self,filepath,filetype=None):

		if filetype is None:

			if self.set_output_file(filepath):
				if self.check_finish_normal():
					res1, lvectors = self.get_final_lvectors()
					res2, lparams  = self.get_final_lparams()
					res3, fatomlist= self.get_final_frac()

					if False not in [res1,res2,res3]:
						# Using 'pymatgen'
						# see docs: https://pymatgen.org/pymatgen.core.html#module-pymatgen.core.lattice
						#self.lattice = Lattice(lvectors)
						#print(self.lattice.abc) - lattice length check
		
						# extracn species-list coord-list (fractional)
						specieslist = []
						coordlist = []
						for item in fatomlist:
							specieslist.append(item[0])
							coordlist.append(item[1:])
							
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

	def get_rdf(self,pair=[None,None],gaussian=False,smearing=0.05):

		try:
			indices_A = [ i for i, site in enumerate(self.struct) if site.species_string == pair[0] ]
			indices_B = [ i for i, site in enumerate(self.struct) if site.species_string == pair[1] ]
		except Exception as e:
			print(f'@Error> in get_rdf(), getting species indices failed -> spcies1: {pair[0]}, species2: {pair[1]}',file=sys.stderr)
			return False, None

		# 
		# Get RadialDistributionFunction -> using vasppy
		if pair[0] == pair[1]:
			rdf = RadialDistributionFunction(structures=[self.struct],indices_i=indices_A)
		else:
			rdf = RadialDistributionFunction(structures=[self.struct],indices_i=indices_A,indices_j=indices_B)
			
		#
		# Using Gaussian smearing ... default smearing factor '0.05'
		#
		if gaussian == True:

			gauss_rdf_r = [ float(i)*0.01 for i in range(1000) ] 	# max distance 10 Anstrom ... 
			gauss_rdf   = [ 0. for i in range(1000) ]

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
	glattice.set_lattice('/Users/woongkyujee/SkukuzaLocal/MultiToolkit/Extractor/demo_gulp_files/A10753/gulp_klmc.gout')
	#glattice.set_lattice('/Users/woongkyujee/SkukuzaLocal/MultiToolkit/Extractor/demo_gulp_files/A15664/gulp_klmc.gout')
	
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
