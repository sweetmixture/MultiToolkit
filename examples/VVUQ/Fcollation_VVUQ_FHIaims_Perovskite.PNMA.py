#!/bin/python

import numpy as np
import os,sys

from Base.UtilsCell import read_fhiaims_cell, find_MX_clusters, find_MX_clusters_pnma, merge_clusters, calculate_delta_d, calculate_sigma_squared, calculate_beta, calculate_beta_pnma, calculate_deltaR
from AppOutputExtractor.FHIaims.FHIaimsOutputExtractor import extractor

if __name__ == '__main__':

	# load original cell no UQ application
	cell0 = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/geometry.centric')

	# load init  - after UQ
	cell_uq = read_fhiaims_cell(sys.argv[1])

	# load final - after optimisation
	cell_final = read_fhiaims_cell(sys.argv[2])

	# sorting by lattice constants : Experimental 20.10.2023
	cell_final = cell_final.sort_lattice()

	# ======
	#	cell_uq - cell0
	# ======
	deltaR, signtable, Rrmsd = calculate_deltaR(cell_uq,cell0)

	# ======
	#	Cell info
	# ======
	lvectors = cell_final.get_lvectors()			# <list:float>[3][3]
	lconstants = cell_final.get_lconstants()		# <list:float>[3]
	langles = cell_final.get_langles()				# <list:float>[3]
	lvolume = cell_final.get_lvolume()				# float

	#clusters = find_MX_clusters(cell_final,M='Pb',X='I')	# find Oh clusters
	clusters = find_MX_clusters_pnma(cell_final,M='Pb',X='I')   # find Oh clusters
	merged_cluster = merge_clusters(clusters)				# merge Oh clusters into 'merged_cluster'

	# beta angles
	#beta_a, beta_b, beta_c = calculate_beta(merged_cluster,C='I',S='Pb')	# beta_x <list:float>[3]
	beta_a, beta_b, beta_c = calculate_beta_pnma(merged_cluster,C='I',S='Pb')   # beta_x <list:float>[3]

	#print(len(beta_a),len(beta_b),len(beta_c))

	# delta d (ddlist)
	ddlist = calculate_delta_d(clusters,C='Pb',S='I')	# ddlist <list:float>[8]

	# sigma squared (sslist)
	sslist = calculate_sigma_squared(clusters,C='Pb',S='I')	# sslist <list:float>[8]


	# ======
	#	output printing
	# ======

	lattice_string = ''

	for item in lconstants:
		lattice_string = lattice_string + '%18.12f,' % (item)
	for item in langles:
		#lattice_string = lattice_string + '%18.12f,' % (item-90.)
		lattice_string = lattice_string + '%18.12f,' % (item)

	lattice_string = lattice_string + '%18.12f,' % (lvolume)

	for item in beta_a:
		lattice_string = lattice_string + '%18.12f,' %(item)
	for item in beta_b:
		lattice_string = lattice_string + '%18.12f,' %(item)
	for item in beta_c:
		lattice_string = lattice_string + '%18.12f,' %(item)
	for item in ddlist:
		lattice_string = lattice_string + '%18.12f,' %(item)
	for item in sslist:
		lattice_string = lattice_string + '%18.12f,' %(item)

	lattice_string = lattice_string + '%18.12f,' % (Rrmsd)

	for item in deltaR:
		lattice_string = lattice_string + '%18.12f,' %(item)
	#print(signtable)
	for item in signtable:
		lattice_string = lattice_string + '%s,' %(item)

	#print(lvectors)

	#print(lconstants)						# 3
	#print(langles)							# 3
	#print(lvolume)							# 1
	#print(beta_a,beta_b,beta_c)			# 12
	#print(ddlist)							# 8
	#print(sslist)							# 8

	#print(deltaR)							# 120
	#print(signtable)						# 120
	#print(Rrmsd)							# 1

	# ======
	#	FHIaims extractor
	# ======
	#outpath = '/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E0.5.3/MoveX/Fsummary/511_aims.out'
	outpath = sys.argv[3]
	ex = extractor()
	ex.set_output_filepath(outpath)

	'''
	    OnSiteE: path: archer2: /work/e05/e05/wkjee/PAX/VVUQ/Perovskite/FHI22_test/222CsPbX/I/elem 
	    CsE = -215367.565781539
	    IE  = -196591.046250619
	    PbE = -590155.339286194
	'''
	CsE = -215367.565781539
	IE  = -196591.046250619
	PbE = -590155.339286194
	OnsiteE = (CsE + PbE + IE * 3.) * 4.

	ex.set_scf_blocks()
	fi_e = ex.get_total_energy() - OnsiteE
	fi_hl= ex.get_homolumo()

	# ======
	#	fi_e	: formation energy
	#	fi_hl[0]: homo
	#	fi_hl[1]: lumo
	# ======
	fhiaims_energy_string = "%.12f,%18.12f,%18.12f,%18.12f," % (fi_e,fi_hl[0],fi_hl[1],fi_hl[1]-fi_hl[0])

	fhiaims_energy_string.strip()
	lattice_string.strip()

	out = fhiaims_energy_string + lattice_string
	print(out)


	#string = ''
	#for i in range(8):
	#	string = string + f'sBx{i+1},sBy{i+1},sBz{i+1},'
	#print(string)


	'''
		Argvs

		sys.argv[1]	:	X_aims_init.in
		sys.argv[2]	:	X_aims_final.in
		sys.argv[3]	:	X_aims.out
	'''
