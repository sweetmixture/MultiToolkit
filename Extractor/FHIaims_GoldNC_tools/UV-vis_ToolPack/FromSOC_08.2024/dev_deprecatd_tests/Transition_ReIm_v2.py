#
# processing state_i ---> state_j transition moment (including Re/Im)
#

from ase.io.cube import read_cube, write_cube
import sys
import numpy as np
from tqdm import tqdm

def get_dens(data,spacing,grid):
	nx,ny,nz = grid
	r = spacing[0]*nx + spacing[1]*ny + spacing[2]*nz
	return r, data[nx,ny,nz]
	# 'r'              : (3,) ndarray
	# 'data[nx,ny,nz]' : wavefunction at [nx,ny,nz] grid point

#
#   i --> f transition handler for the case including spin-up/dn + SOC coupling (i.e., handling eigenstate formed of 'real' + 'imag')
#
def get_trans_int_full(icube_filelist,fcube_filelist,verbose=False):

	# final returns
	tint = 0.                              # transition intensity (real)
	trans_moment_re = np.array([0.,0.,0.]) # transition moment (real)
	trans_moment_im = np.array([0.,0.,0.]) # transition moment (imag)
	integral = 0. # for checking

	# contents check
	print(f'input state_i: {icube_filelist}')
	print(f'input state_f: {fcube_filelist}')

	# * * * CONVENTION * * *
	#
	# icube_filelist = [ ci_real_up, ci_imag_up, ci_real_dn, ci_imag_dn ] <<< EXPECTED FORMAT !!!
	# fcube_filelist = [ cf_real_up, cf_imag_up, cf_real_dn, cf_imag_dn ] <<< EXPECTED FORMAT !!!
	#
	with open(icube_filelist[0],'r') as ciru, open(icube_filelist[1],'r') as ciiu, \
		 open(icube_filelist[2],'r') as cird, open(icube_filelist[3],'r') as ciid:
		 # c (coefficient) i (initial state) r (real) u (spin-up)
		 # c (coefficient) i (initial state) i (imag) u (spin-up)
		 # c (coefficient) i (initial state) r (real) d (spin-dn)
		 # c (coefficient) i (initial state) i (imag) d (spin-dn)

		icubelist = [ read_cube(ciru,read_data=True,verbose=True), read_cube(ciiu,read_data=True,verbose=True),
					  read_cube(cird,read_data=True,verbose=True), read_cube(ciid,read_data=True,verbose=True) ]

	with open(fcube_filelist[0],'r') as cfru, open(fcube_filelist[1],'r') as cfiu, \
		 open(fcube_filelist[2],'r') as cfrd, open(fcube_filelist[3],'r') as cfid:
		 # c (coefficient) f (final   state) r (real) u (spin-up)
		 # c (coefficient) f (final   state) i (imag) u (spin-up)
		 # c (coefficient) f (final   state) r (real) d (spin-dn)
		 # c (coefficient) f (final   state) i (imag) d (spin-dn)
		fcubelist = [ read_cube(cfru,read_data=True,verbose=True), read_cube(cfiu,read_data=True,verbose=True),
					  read_cube(cfrd,read_data=True,verbose=True), read_cube(cfid,read_data=True,verbose=True) ]

	# contents check
	print(f' * loading finished')

	#
	# Extracting: [1] grid [2] spacing [3] data
	#
	igridlist = []      # grid info of [ ciru, ciiu, cird, ciid ]
	fgridlist = []      # grid info of [ cfru, cfiu, cfrd, cfid ]
	ispacinglist = []   # ...
	fspacinglist = []   #
	idatalist = []      #
	fdatalist = []      #

	for icube,fcube in zip(icubelist,fcubelist):

		igridlist.append(icube['data'].shape)
		ispacinglist.append(icube['spacing'])
		idatalist.append(icube['data'])

		fgridlist.append(fcube['data'].shape)
		fspacinglist.append(fcube['spacing'])
		fdatalist.append(fcube['data'])

	# contents checking
	#print(igridlist)
	#print(fgridlist)
	#print(ispacinglist)
	#print(fspacinglist)

	nx_max = igridlist[0][0]
	ny_max = igridlist[0][1]
	nz_max = igridlist[0][2]

	#
	# grid setting
	#
	for nx in range(nx_max):
		
		#
		# process checker
		if nx%20 == 0:
			print(f'{nx:4d}',end='',flush=True)

		for ny in range(ny_max):
			for nz in range(nz_max):

				# obtain grid
				grid = (nx,ny,nz)

				# get position vector: use get_dens(data,spacing,grid): return r, data[nx,ny,nz]
				ir, iru = get_dens(idatalist[0],ispacinglist[0],grid)	# real up (i)
				ir, iiu = get_dens(idatalist[1],ispacinglist[1],grid)	# imag up (i)
				ir, ird = get_dens(idatalist[2],ispacinglist[2],grid)	# real dn (i)
				ir, iid = get_dens(idatalist[3],ispacinglist[3],grid)	# imag dn (i)

				fr, fru = get_dens(fdatalist[0],fspacinglist[0],grid)	# real up (f)
				fr, fiu = get_dens(fdatalist[1],fspacinglist[1],grid)	# imag up (f)
				fr, frd = get_dens(fdatalist[2],fspacinglist[2],grid)	# real dn (f)
				fr, fid = get_dens(fdatalist[3],fspacinglist[3],grid)	# imag dn (f)

				# --------------------------------------
				# * calculate Si†⋅r⋅Sf
				#
				# where Si = [ Si↑ ] ,
				#            [ Si↓ ]
				# and
				# Si↑ = Ψi↑_Re + I*Ψi↑_Im
				# Si↓ = Ψi↓_Re + I*Ψi↓_Im
				# --------------------------------------
				re = iru*fru + iiu*fiu + ird*frd + iid*fid	# transition moment Re(M) : Si†Sf part
				im = iru*fiu - iiu*fru + ird*fid - iid*frd	# transition moment Im(M) : Si†Sf part

				rre = ir * re
				rim = ir * im

				trans_moment_re += rre
				trans_moment_im += rim

				# integral check
				integral += re**2. + im**2.

	tint = rre[0]**2. + rim[0]**2. + rre[1]**2. + rim[1]**2. + rre[2]**2. + rim[2]**2.

	print(f'Integral: {integral}')
	return tint, (trans_moment_re,trans_moment_im)

def get_trans_int(icube,fcube,verbose=False):

	tint = 0.
	trans_dipole = np.array([0.,0.,0.])

	# creat icube_obj
	with open(icube, 'r') as fileobj:
		icube_obj = read_cube(fileobj,read_data=True,verbose=True)
	if verbose:
		print(f' * loading initial cube done : {icube}')
	# creat fcube_obj
	with open(fcube, 'r') as fileobj:
		fcube_obj = read_cube(fileobj,read_data=True,verbose=True)
	if verbose:
		print(f' * loading final   cube done : {fcube}')
	'''
		* 'atoms': Atoms object
		* 'data' : (Nx, Ny, Nz) ndarray
		* 'origin': (3,) ndarray, specifying the cube_data origin.
		* 'spacing': (3, 3) ndarray, representing voxel size
	'''
	igrid = icube_obj['data'].shape    # icube grid shape
	fgrid = fcube_obj['data'].shape    # fcube grid shape
	ispacing = icube_obj['spacing']    # icube grid spacing (similar to lattice vectors, if orthogonal axes then non diagonal elements are '0')
	fspacing = fcube_obj['spacing']    # fcube grid spacing
	idata = icube_obj['data']          # icube volumetric data e.g., electron density
	fdata = fcube_obj['data']          # fcube volumentic data

	#
	# ADD grid checking / spacing checking : for portability later (written, 05.2024 - WKJEE)
	#
	nx_max = igrid[0]
	ny_max = igrid[1]
	nz_max = igrid[2]

	for nx in range(nx_max):
	#for nx in tqdm(range(nx_max), desc='Integral progress'):

		# marking or monitoring the process - printing
		if nx%20 == 0:
			print(f'{nx:4d}',end='',flush=True)

		for ny in range(ny_max):
			for nz in range(nz_max):
				# get grid - or spatial position 'r' vector or (x,y,z)
				grid = (nx,ny,nz)

				# get position vector: ir/fr and elec densities: idesn/fdens
				# here, ir and fr should be the same for the same cubefile (using aims default)
				ir, idens = get_dens(idata,ispacing,grid)
				fr, fdens = get_dens(fdata,ispacing,grid)

				# IMPORTANT !!!
				#
				# Multiplication of Energy (wI) has not been done at this stage!, note, FI = 2/3 wI p^2
				#
				# sig = np.linalg.norm(ir * idens * fdens)**2. -------> not correct !
				# tint += sig
				# ------------------------
				# trans_dipole = psi_i(nx,ny,nz) * (nx,ny,nz) * psi_f(nx,ny,nz)
				#
				trans_dipole += (ir * idens * fdens)

	tint = np.linalg.norm(trans_dipole)**2.

	return tint

if __name__ == '__main__':

	# tested
	icube = 'spin_up_0_HOMO.cube'
	fcube = 'spin_down_0_LUMO.cube'
	# 100.90013832731726 -----> Error? forbidden transition?

	icube = 'spin_up_0_HOMO.cube'
	fcube = 'spin_up_0_LUMO.cube'
	# 6.337018652034545

	icube = 'spin_down_0_HOMO.cube'
	fcube = 'spin_down_0_LUMO.cube'
	# 27.533396845080475

	icube = 'spin_down_0_HOMO.cube'
	fcube = 'spin_down_1_LUMO.cube'
	# 1.7952633115740475

	icube = 'spin_down_0_HOMO.cube'
	fcube = 'spin_down_2_LUMO.cube'
	# 1.2700516331437115

	icube = 'spin_down_0_HOMO.cube'
	fcube = 'spin_down_3_LUMO.cube'
	# 66.1973286387213


	print(' * Tansition Dipole Test')
	#transI = get_trans_int(icube,fcube,verbose=True)
	#print(transI)

	# test
	icubelist = ['cube_037_eigenstate_03109_spin_1.cube','cube_038_eigenstate_imag_03109_spin_1.cube',
				 'cube_039_eigenstate_03109_spin_2.cube','cube_040_eigenstate_imag_03109_spin_2.cube']
	fcubelist = ['cube_037_eigenstate_03109_spin_1.cube','cube_038_eigenstate_imag_03109_spin_1.cube',
				 'cube_039_eigenstate_03109_spin_2.cube','cube_040_eigenstate_imag_03109_spin_2.cube']

	tint, tmo = get_trans_int_full(icubelist,fcubelist)
	print(tint,tmo)

'''
	Expected Output:

	* Tansition Dipole Test
	input state_i: ['cube_037_eigenstate_03109_spin_1.cube', 'cube_038_eigenstate_imag_03109_spin_1.cube', 'cube_039_eigenstate_03109_spin_2.cube', 'cube_040_eigenstate_imag_03109_spin_2.cube']
	input state_f: ['cube_037_eigenstate_03109_spin_1.cube', 'cube_038_eigenstate_imag_03109_spin_1.cube', 'cube_039_eigenstate_03109_spin_2.cube', 'cube_040_eigenstate_imag_03109_spin_2.cube']
	* loading finished
	0  20  40  60  80 100 120 140 160 180 200 220 240 260Integral: 10.395671519065049
	0.0 (array([14206.05329116, 12476.55015189, 12713.47303407]), array([0., 0., 0.]))
	
	trans moment = 0 since same eigenstate used
	Im trans_moment = 0 since same eigenstate used
'''
