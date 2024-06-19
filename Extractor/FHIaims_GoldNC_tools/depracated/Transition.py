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
	transI = get_trans_int(icube,fcube,verbose=True)
	print(transI)
