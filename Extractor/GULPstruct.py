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

    using pymatgen / vasppy ?

'''

import os,sys
import numpy as np

from pymatgen.core import Lattice,Structure
#from Extractor.GULP import GULP_Patterns
from Extractor.GULP import ExtractGULP


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
						#print(self.struct.lattice.abc)
						#print(self.struct.lattice.angles)

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

if __name__=='__main__':

	glattice = GULPLattice()
	glattice.set_lattice('/work/e05/e05/wkjee/Software/MultiToolkit/Extractor/gulp.got')	# upto here, setting pymatgen lattice : member_variable(propery) -> struct


	# rdf implementation reference : https://vasppy.readthedocs.io/en/latest/examples/rdfs.html

