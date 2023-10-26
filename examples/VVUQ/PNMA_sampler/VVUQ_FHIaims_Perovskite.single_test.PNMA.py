#!/bin/python

import numpy as np
import os,sys

from Base.UtilsCell import read_fhiaims_cell, find_MX_clusters,find_MX_clusters_pnma, merge_clusters, calculate_delta_d, calculate_sigma_squared, calculate_beta, calculate_beta_pnma, calculate_deltaR
from AppOutputExtractor.FHIaims.FHIaimsOutputExtractor import extractor

if __name__ == '__main__':

	# load original cell no UQ application
	cell0 = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveA/summary_1-237/aims_init.in')

	# load init  - after UQ
	#cell_uq = read_fhiaims_cell(sys.argv[1])
	cell_uq = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E0.5.3/MoveX/Fsummary/511_aims_init.in')

	# load final - after optimisation
	#cell_final = read_fhiaims_cell(sys.argv[2])
	#cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E0.5.3/MoveX/Fsummary/511_aims_final.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E0.5.3/MoveX/Fsummary/87_aims_final.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/geometry.centric')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveB/local_33/run__fe8h0tno/runs/run_10/geometry.in.next_step')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveA/local_10/run__ta2gwpz6/runs/run_4/geometry.in.next_step')
	#cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveB/Fsummaray1/410_aims_final.in')
	#cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveA/Fsummary1/1_aims_final.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveA/Fsummary1/5_aims_final.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveA/Fsummary1/6_aims_final.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveA/Fsummary1/7_aims_final.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveA/Fsummary1/9_aims_final.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveA/Fsummary1/12_aims_final.in')
	print('* * * before rotation')
	print(cell_final.get_lvectors())
	print(cell_final.get_lconstants())
	print(cell_final.get_langles())

	#print('test')
	#
	#	lattice vector sorting test  : see '/work/e05/e05/wkjee/Software/MultiToolkit/Base/single_test'
	#

	cell_final = cell_final.sort_lattice()
	print('rotation reference')
	print(cell_final.sort_lattice_reference)

	print('* * * after rotation')
	print(cell_final.get_lvectors())
	print(cell_final.get_lconstants())
	print(cell_final.get_langles())
	#print('test END')

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
	clusters = find_MX_clusters_pnma(cell_final,M='Pb',X='I')	# find Oh clusters

	#for cluster in clusters:
	#	cluster.write_xyz(stdout=True)

	merged_cluster = merge_clusters(clusters)				# merge Oh clusters into 'merged_cluster'

	cell_final.write_fhiaims(stdout=True)
	cell_final.write_xyz(stdout=True)
	print('--- config done')
	merged_cluster.write_xyz(stdout=True)

	# beta angles
	#beta_a, beta_b, beta_c = calculate_beta(merged_cluster,C='I',S='Pb')	# beta_x <list:float>[3]
	beta_a, beta_b, beta_c = calculate_beta_pnma(merged_cluster,C='I',S='Pb')	# beta_x <list:float>[3]

	print(len(beta_a),len(beta_b),len(beta_c))

	# delta d (ddlist)
	ddlist = calculate_delta_d(clusters,C='Pb',S='I')	# ddlist <list:float>[8]

	# sigma squared (sslist)
	sslist = calculate_sigma_squared(clusters,C='Pb',S='I')	# sslist <list:float>[8]


	# ======
	#	output printing
	# ======

	print('OUTPUT PRINTING -------------------')
	print(lvectors)
	print(lconstants)
	print(langles)
	print(lvolume)
	print(beta_a,beta_b,beta_c)
	print(ddlist)
	print(sslist)

	#print(deltaR)
	#print(signtable)
	#print(Rrmsd)


	# ======
	#	FHIaims extractor
	# ======
	outpath = '/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Pnma_sqrt_reduced_cell/Move_Atoms_E1.3/MoveB/Fsummaray1/410_aims.out'
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
	fhiaims_energy_string = "%18.12f,%18.12f,%18.12f,%18.12f," % (fi_e,fi_hl[0],fi_hl[1],fi_hl[1]-fi_hl[0])

	print(fhiaims_energy_string)

