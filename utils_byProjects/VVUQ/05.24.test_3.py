##
## loading and manipulating structures
##
from Base.UtilsCell import read_fhiaims_cell, find_MX_clusters, merge_clusters, get_distance, cluster_dump_excessX, calculate_delta_d
##
## calculating geometric features
##
from Base.UtilsCell import calculate_delta_d, calculate_sigma_squared, calculate_beta, calculate_deltaR
##
from Supporting import print_delta_r, print_delta_r_sign

import sys

# select test set
_test_set = 'B'
#_test_set = 'A'

print(f' ! ------------------------')
print(f' ! Loading MultiToolkit API')
print(f' ! ------------------------')
print(f' ! test_set: {_test_set}')

# ----- SET A
if _test_set == 'A':
	cell_0     = read_fhiaims_cell('/work/e05/e05/wkjee/Software/MultiToolkit/examples/CsPbI3.in')
	cell_uq    = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveA/Fsummary/1_aims_init.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveA/Fsummary/1_aims_final.in')
# ----- SET B
elif _test_set == 'B':
	cell_0     = read_fhiaims_cell('/work/e05/e05/wkjee/Software/MultiToolkit/examples/CsPbI3.in')
	cell_uq    = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveB/Fsummary/1_aims_init.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveB/Fsummary/1_aims_final.in')
# ----- SET X
elif _test_set == 'X':
	cell_0     = read_fhiaims_cell('/work/e05/e05/wkjee/Software/MultiToolkit/examples/CsPbI3.in')
	cell_uq    = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveX/Fsummary/1_aims_init.in')
	cell_final = read_fhiaims_cell('/work/e05/e05/wkjee/PAX/VVUQ/Perovskite/UQ_CsPbI/Move_Atoms_E1.3/MoveX/Fsummary/1_aims_final.in')

print(f' ! file loading done')

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
#deltaR, signtable, Rrmsd = calculate_deltaR(cell_uq,cell_0)
#print(deltaR)
#print(signtable)
#print(Rrmsd)

# ======
#   Cell info
# ======
#lvectors = cell_final.get_lvectors()            # <list:float>[3][3]
#lconstants = cell_final.get_lconstants()        # <list:float>[3]
#langles = cell_final.get_langles()              # <list:float>[3]
#lvolume = cell_final.get_lvolume()              # float

#
# retrieving : local AX / BX clusters : AX12 (8) / BX6 (8)
#
print(f' * retrieving cluster AX12 (8) / BX6 (8)')
bx_cluster_0 = cluster_dump_excessX(find_MX_clusters(cell_0,M='Pb',X='I',cutd=8.0),6)
bx_cluster_uq = cluster_dump_excessX(find_MX_clusters(cell_uq,M='Pb',X='I',cutd=8.0),6)
bx_cluster_final = cluster_dump_excessX(find_MX_clusters(cell_final,M='Pb',X='I',cutd=8.0),6)
print(f' ! loading BX finshed')
ax_cluster_0 = cluster_dump_excessX(find_MX_clusters(cell_0,M='Cs',X='I',cutd=8.0),12)
ax_cluster_uq = cluster_dump_excessX(find_MX_clusters(cell_uq,M='Cs',X='I',cutd=8.0),12)
ax_cluster_final = cluster_dump_excessX(find_MX_clusters(cell_final,M='Cs',X='I',cutd=8.0),12)
print(f' ! loading AX finshed')
#
# clusters merging --- prefix 'f'
#
print(f' * creating merged clusters')
fbx_cluster_0 = merge_clusters(bx_cluster_0)
fbx_cluster_uq = merge_clusters(bx_cluster_uq)
fbx_cluster_final = merge_clusters(bx_cluster_final)
print(f' ! total BX clusters: 0, uq, final done')
fax_cluster_0 = merge_clusters(ax_cluster_0)
fax_cluster_uq = merge_clusters(ax_cluster_uq)
fax_cluster_final = merge_clusters(ax_cluster_final)
print(f' ! total AX clusters: 0, uq, final done')
#
# clusters merging Done ---
#

#
# printing merged BX cluster
#
print('* full fbx0 writing xyz ...')
#fbx_cluster_0.write_xyz(stdout=True)
fbx_cluster_0.write_xyz(name='bx0.xyz')
print('* full fbxuq writing xyz ...')
#fbx_cluster_uq.write_xyz(stdout=True)
fbx_cluster_uq.write_xyz(name='bxuq.xyz')
print('* full fbxuq_final writing xyz ...')
#fbx_cluster_final.write_xyz(stdout=True)
fbx_cluster_final.write_xyz(name='bxuqf.xyz')

#
# printing merged AX cluster
#
print('* full fax0 writing xyz ...')
#fax_cluster_0.write_xyz(stdout=True)
fax_cluster_0.write_xyz(name='ax0.xyz')
print('* full faxuq writing xyz ...')
#fax_cluster_uq.write_xyz(stdout=True)
fax_cluster_uq.write_xyz(name='axuq.xyz')
print('* full faxuq_final writing xyz ...')
#fax_cluster_final.write_xyz(stdout=True)
fax_cluster_final.write_xyz(name='axuqf.xyz')

"""
	Now obtined

	AX12 :                         Merged
			ax_cluster_0         : fax_cluster_0
			ax_cluster_uq        : fax_cluster_uq
			ax_cluster_final     : fax_cluster_final

	BX6  :                         Merged
			bx_cluster_0         : fbx_cluster_0
			bx_cluster_uq        : fbx_cluster_uq
			bx_cluster_final     : fbx_cluster_final
"""

_mark0  = '0'
_markuq = 'uq'
_markuqf= 'uqf'
#
# calculate delta_d : return <list:float>[8]
#
# delta_d obtained for: Cs-I; Ih 12 bonds
#
_ax_bond_cnt = 12
ax_cluster_0_dd = calculate_delta_d(ax_cluster_0,bond_cnt=_ax_bond_cnt,C='Cs',S='I')	# this will return a list of 8 numbers (for each 'Cs')
ax_cluster_uq_dd = calculate_delta_d(ax_cluster_uq,bond_cnt=_ax_bond_cnt,C='Cs',S='I')
ax_cluster_final_dd = calculate_delta_d(ax_cluster_final,bond_cnt=_ax_bond_cnt,C='Cs',S='I')
print(f'* Δd values for AX')
print(f'{_mark0:>20s}{_markuq:>20s}{_markuqf:>20s}')
for d0, duq, duqf in zip(ax_cluster_0_dd,ax_cluster_uq_dd,ax_cluster_final_dd):
	print(f'{d0:20.12e}{duq:20.12e}{duqf:20.12e}')

#
# delta_d obtained for: Pb-I; Oh 6 bonds
#
_bx_bond_cnt = 6
bx_cluster_0_dd = calculate_delta_d(bx_cluster_0,bond_cnt=_bx_bond_cnt,C='Pb',S='I')	# this will return a list of 8 numbers (for each 'Pb')
bx_cluster_uq_dd = calculate_delta_d(bx_cluster_uq,bond_cnt=_bx_bond_cnt,C='Pb',S='I')
bx_cluster_final_dd = calculate_delta_d(bx_cluster_final,bond_cnt=_bx_bond_cnt,C='Pb',S='I')
print(f'* Δd values for BX')
print(f'{_mark0:>20s}{_markuq:>20s}{_markuqf:>20s}')
for d0, duq, duqf in zip(bx_cluster_0_dd,bx_cluster_uq_dd,bx_cluster_final_dd):
	print(f'{d0:20.12e}{duq:20.12e}{duqf:20.12e}')





#
# calculate beta angles: return
# ㄴMultiToolkit/Base/UtilsCell.py
#
#                        'full cluster used'
#     def calculate_beta(cluster,C='',S='',cutd=4.0):
#         ...
#         return beta_a, beta_b, beta_c # <list:float>[4] each
#
print(f'')
print(f'### ------------------------------')
print(f'### calculating β angles: B-X-B') # i.e. Pb-I-Pb
print(f'### ------------------------------')

_x_direction = 'x[a]'
_y_direction = 'y[b]'
_z_direction = 'z[c]'
beta_x, beta_y, beta_z = calculate_beta(fbx_cluster_0,C='I',S='Pb')
print(f'* β angles: 0')
print(f'{_x_direction:>20s}{_y_direction:>20s}{_z_direction:>20s}')
for bx, by, bz in zip(beta_x,beta_y,beta_z):
	print(f'{bx:20.12e}{by:20.12e}{bz:20.12e}')
beta_x, beta_y, beta_z = calculate_beta(fbx_cluster_uq,C='I',S='Pb')
print(f'* β angles: uq')
print(f'{_x_direction:>20s}{_y_direction:>20s}{_z_direction:>20s}')
for bx, by, bz in zip(beta_x,beta_y,beta_z):
	print(f'{bx:20.12e}{by:20.12e}{bz:20.12e}')
beta_x, beta_y, beta_z = calculate_beta(fbx_cluster_final,C='I',S='Pb')
print(f'* β angles: uqf')
print(f'{_x_direction:>20s}{_y_direction:>20s}{_z_direction:>20s}')
for bx, by, bz in zip(beta_x,beta_y,beta_z):
	print(f'{bx:20.12e}{by:20.12e}{bz:20.12e}')


# sys.exit()


###
### * Applying No lattice Sorting/Rotation
###
#deltaR, signtable, Rrmsd = calculate_deltaR(cell_uq,cell0)
#print(deltaR)
#print(signtable)
#print(Rrmsd)

###
### get cell info : note. 'lvectors_*' ---> [ v1 v2 v3 ]   column vector format 3x3 list
###
print(f' * TESTING Cell Info - 0 ')
lvectors_0   = cell_0.get_lvectors()    # <list:float>[3][3]
lconstants_0 = cell_0.get_lconstants()  # <list:float>[3]
langles_0    = cell_0.get_langles()     # <list:float>[3]
lvolume_0    = cell_0.get_lvolume()     # float
print(f' lvectors   : {lvectors_0}')
print(f' lconstants : {lconstants_0}')
print(f' langles    : {langles_0}')
print(f' lvolume    : {lvolume_0}')

print(f' * TESTING Cell Info - UQ ')
lvectors_uq   = cell_uq.get_lvectors()    # <list:float>[3][3]
lconstants_uq = cell_uq.get_lconstants()  # <list:float>[3]
langles_uq    = cell_uq.get_langles()     # <list:float>[3]
lvolume_uq    = cell_uq.get_lvolume()     # float
print(f' lvectors   : {lvectors_uq}')
print(f' lconstants : {lconstants_uq}')
print(f' langles    : {langles_uq}')
print(f' lvolume    : {lvolume_uq}')

print(f' * TESTING Cell Info - FINAL ')
lvectors_final   = cell_final.get_lvectors()    # <list:float>[3][3]
lconstants_final = cell_final.get_lconstants()  # <list:float>[3]
langles_final    = cell_final.get_langles()     # <list:float>[3]
lvolume_final    = cell_final.get_lvolume()     # float
print(f' lvectors   : {lvectors_final}')
print(f' lconstants : {lconstants_final}')
print(f' langles    : {langles_final}')
print(f' lvolume    : {lvolume_final}')

### ----------------
### INPUT SETTING (tentative - 02.05.2024 Thur)
### ----------------
### total 120 (3 X 40) input variables
###
### Parsed Input : Cell(uq) - Cell(0) : Cartesian (Å) unit
###
elemlist, p_input_uq0_dr, p_input_uq0_sign, p_input_uq0_rmsd = calculate_deltaR(cell_uq,cell_0,elem=True)
print(f' * TESTING Cell uq - Cell 0 : delta_r')
print_delta_r(p_input_uq0_dr,elemlist=elemlist)
print(f' * ctd ... show sign table') # sign table -> -1/+1 binary !!
print_delta_r_sign(p_input_uq0_sign,elemlist=elemlist)

### CONVERSION TO JSON?


