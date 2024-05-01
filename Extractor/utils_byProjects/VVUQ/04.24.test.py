from Base.UtilsCell import read_fhiaims_cell, calculate_deltaR, find_MX_clusters, merge_clusters, get_distance, cluster_dump_excessX
import sys


# ----- Refactoring 
cell0      = read_fhiaims_cell('/work/e05/e05/wkjee/Software/MultiToolkit/examples/CsPbI3.in')
cell_uq    = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveA/Fsummary/1_aims_init.in')
cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveA/Fsummary/1_aims_final.in')

# after 'read_fhiaims_cell()'
# cell.lvectors   set
# cell.lconstatns set
# cell.langles    set
#
# if 'atom_frac' used & if 'atom' used (cartesian)
#
# cell.atomlist<list<Atom<class>>> set
#

# ----- Test -----
#print(cell.get_lvectors())         # [ v1 v2 v3 ]   column vector format 3x3 list
#print(cell.get_lattice_matrix())   # [ v1 v2 v3 ]^T transposed lvectors  3x3 list ----> FHIaims *.in file convention
#print(cell.get_lconstants())       # <list>
#print(cell.get_langles())          # <list>
#print(cell.get_lvolume())          # <float>
# * show atom info
#for atom in cell.get_atoms():
#	#print(atom.get_element(),atom.get_cart(),atom.get_frac())
#	print(atom.print_atom(mode='frac_fhiaims'))


###
### * Applying No lattice Sorting/Rotation
###
deltaR, signtable, Rrmsd = calculate_deltaR(cell_uq,cell0)
#print(deltaR)
#print(signtable)
#print(Rrmsd)

# ======
#   Cell info
# ======
lvectors = cell_final.get_lvectors()            # <list:float>[3][3]
lconstants = cell_final.get_lconstants()        # <list:float>[3]
langles = cell_final.get_langles()              # <list:float>[3]
lvolume = cell_final.get_lvolume()              # float

###
### AX (8) / BX (12) clusters : cell_final
###

# BX cluster check
f_clusters_bx = find_MX_clusters(cell_final,M='Pb',X='I')    # find Oh clusters
f_total_cluster_bx = merge_clusters(f_clusters_bx)               # merge Oh clusters into 'merged_cluster'
print(f' ---- print total BX cluster octahedrons')
f_total_cluster_bx.write_xyz(stdout=True)

# AX cluster check
f_clusters_ax = find_MX_clusters(cell_final,M='Cs',X='I',cutd=8.0)
# dump X if total: Xn > 13, for AXs clusters
for cluster in f_clusters_ax:
	# centric atom: this case 'A' atom
	centric_atom = cluster.get_atoms()[0]
	# if there are more than 12 X in the cluster ... specific case only works for this!
	while cluster.get_number_of_atoms() > 13:

		dist_list = []
		for atom in cluster.get_atoms():

			if atom.get_element() == centric_atom.get_element():	# skip if 'Cs'
				pass
			else:
				dist_list.append( get_distance(centric_atom,atom) )
		max_index = dist_list.index(max(dist_list))
		cluster.del_atom(max_index+1)

f_total_cluster_ax = merge_clusters(f_clusters_ax)
print(f' ---- print AX cluster dodecahedron')
f_total_cluster_ax.write_xyz(stdout=True)
#clusters_ax = find_MX_clusters(cell0,M='Cs',X='I',cutd=5.0) # formign dodecahedron CsI12
#for cluster in clusters_ax:
#	cluster.write_xyz(stdout=True)

###
### AX (8) / BX (12) clusters : cell0 / cell_uq
###
uq_clusters_ax = find_MX_clusters(cell_uq,M='Cs',X='I',cutd=8.0)
uq_clusters_ax = cluster_dump_excessX(uq_clusters_ax, 12)
uq_total_cluster_ax = merge_clusters(uq_clusters_ax)
print(f' ---- print UQ_AX cluster dodecahedorn')
uq_total_cluster_ax.write_xyz(stdout=True)

clusters_ax = find_MX_clusters(cell0,M='Cs',X='I',cutd=8.0)
clusters_ax = cluster_dump_excessX(clusters_ax, 12)
total_cluster_ax = merge_clusters(clusters_ax)
print(f' ---- print 0_AX cluster dodecahedron')
total_cluster_ax.write_xyz(stdout=True)



