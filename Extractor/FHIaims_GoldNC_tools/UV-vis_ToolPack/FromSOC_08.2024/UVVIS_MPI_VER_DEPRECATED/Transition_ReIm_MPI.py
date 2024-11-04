#
# processing state_i ---> state_j transition moment (including Re/Im)
#

from ase.io.cube import read_cube, write_cube
import sys, time
import numpy as np
from tqdm import tqdm

#
#	MPI Extension
#
from mpi4py import MPI

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
	#print(f'input state_i: {icube_filelist}')
	#print(f'input state_f: {fcube_filelist}')

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
	#print(f' * loading finished')

	#
	# Extracting: [1] grid [2] spacing [3] data
	#
	igridlist = []      # grid info of [ ciru, ciiu, cird, ciid ]	: element grid is (nx,ny,nz) object by data.shape 
	fgridlist = []      # grid info of [ cfru, cfiu, cfrd, cfid ]
	ispacinglist = []   # ...
	fspacinglist = []   #
	idatalist = []      # data is numpy.ndarray with shape (nx,ny,nz)
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
		if nx%50 == 0:
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

	#tint = rre[0]**2. + rim[0]**2. + rre[1]**2. + rim[1]**2. + rre[2]**2. + rim[2]**2. # >>>>> ERROR
	tint = trans_moment_re[0]**2. + trans_moment_im[0]**2. \
		 + trans_moment_re[1]**2. + trans_moment_im[1]**2. \
		 + trans_moment_re[2]**2. + trans_moment_im[2]**2.

	#print(f'Integral: {integral}')
	return tint, (trans_moment_re,trans_moment_im)


# ------------------------------------------------------------------------------------
# i --> f transition handler for the case including spin-up/dn + SOC coupling (i.e., handling eigenstate formed of 'real' + 'imag')
# MPI EXTENSION
# ------------------------------------------------------------------------------------
def get_trans_int_full_mpi(icube_filelist,fcube_filelist,comm,verbose=False):

	rank = comm.Get_rank() # get MPI rank
	size = comm.Get_size() # get MPI size (#procs)
	
	#
	# final returns : final all_reduce destination
	#
	tint = 0.                              # transition intensity (real)
	trans_moment_re = np.array([0.,0.,0.]) # transition moment (real)
	trans_moment_im = np.array([0.,0.,0.]) # transition moment (imag)
	integral = 0. # for checking

	# local copies for each procs
	local_tint = 0.
	local_trans_moment_re = np.array([0.,0.,0.])
	local_trans_moment_im = np.array([0.,0.,0.])
	local_integral = 0.

	# contents check
	#print(f'input state_i: {icube_filelist}')
	#print(f'input state_f: {fcube_filelist}')

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
	if rank == 0:
		print(f' *loading finished*\t',end="",flush=True)

	#
	# Extracting: [1] grid [2] spacing [3] data
	#
	igridlist = []      # grid info of [ ciru, ciiu, cird, ciid ]	: element grid is (nx,ny,nz) object by data.shape 
	fgridlist = []      # grid info of [ cfru, cfiu, cfrd, cfid ]
	ispacinglist = []   # ...
	fspacinglist = []   #
	idatalist = []      # data is numpy.ndarray with shape (nx,ny,nz)
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

	total_points = nx_max * ny_max * nz_max
	
	# block-decomposition algorithm
	points_per_proc = total_points // size
	remainder = total_points % size

	if rank < remainder:
		start_index = rank * (points_per_proc + 1)
		end_index   = start_index + points_per_proc + 1
	else:
		start_index = rank * points_per_proc + remainder
		end_index   = start_index + points_per_proc

	comm.Barrier()

	for index in range(start_index,end_index):

		# recover nx, ny, nz as before stratified : algorithm below works for triple loops
		nx = index // (ny_max * nz_max)
		ny = (index // nz_max) % ny_max
		nz = index % nz_max

		# marking or monitoring the process - printing
		#if nx%50 == 0 and ny == 0 and nz == 0:
		#	if rank == 0:
	 	#		print(f'{nx:4d} ',end='',flush=True)

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

		local_trans_moment_re += rre
		local_trans_moment_im += rim

		# integral check
		local_integral += re**2. + im**2.

	comm.Barrier()

	#local_tint =   local_trans_moment_re[0]**2. + local_trans_moment_im[0]**2. \
	#        	 + local_trans_moment_re[1]**2. + local_trans_moment_im[1]**2. \
	#        	 + local_trans_moment_re[2]**2. + local_trans_moment_im[2]**2.
	#
	# this dot product must be done after MPI_Reduce
	#

	#
	# MPI Reduce
	#
	#tint = comm.reduce(local_tint,op=MPI.SUM,root=0)
	trans_moment_re = comm.reduce(local_trans_moment_re,op=MPI.SUM,root=0)
	trans_moment_im = comm.reduce(local_trans_moment_im,op=MPI.SUM,root=0)
	integral = comm.reduce(local_integral,op=MPI.SUM,root=0)
	comm.Barrier()

	if rank == 0: # since above using 'reduce', therefore rest of procs will see, trans_moment_re/im as None type object; must within rank == 0
		tint = trans_moment_re[0]**2. + trans_moment_im[0]**2. \
			 + trans_moment_re[1]**2. + trans_moment_im[1]**2. \
			 + trans_moment_re[2]**2. + trans_moment_im[2]**2.

	#
	# causing dead-lock?? 15.08 check
	#del icubelist
	#del fcubelist
	#del idatalist
	#del fdatalist

	comm.Barrier()

	#print(f'Integral: {integral}')

	#
	# at this point, only 'root' proc has the correct values
	#
	return tint, (trans_moment_re,trans_moment_im)


# ------------------------------------------------------------------------------------
#	Serial for No-SOC, No-Periodic : i.e., NO imag eigenstate
# ------------------------------------------------------------------------------------
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
			print(f'{nx:4d} ',end='',flush=True)

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


	# --------------------------------------------------------------------------------------------------------
	# Below this point, only MPI adapted code
	# --------------------------------------------------------------------------------------------------------

	comm = MPI.COMM_WORLD
	rank = comm.Get_rank()
	size = comm.Get_size()

	if rank == 0:
		print(f' * MPI - Tansition Dipole Test : nprocs: {size}')
	
	#transI = get_trans_int(icube,fcube,verbose=True)
	#print(transI)

	# test
	#icubelist = ['cube_037_eigenstate_03109_spin_1.cube','cube_038_eigenstate_imag_03109_spin_1.cube','cube_039_eigenstate_03109_spin_2.cube','cube_040_eigenstate_imag_03109_spin_2.cube']
	icubelist = ['cube_017_eigenstate_03104_spin_1.cube', 'cube_018_eigenstate_imag_03104_spin_1.cube', 'cube_019_eigenstate_03104_spin_2.cube', 'cube_020_eigenstate_imag_03104_spin_2.cube']

	#fcubelist = ['cube_037_eigenstate_03109_spin_1.cube','cube_038_eigenstate_imag_03109_spin_1.cube',
	#			 'cube_039_eigenstate_03109_spin_2.cube','cube_040_eigenstate_imag_03109_spin_2.cube']
	
	#fcubelist = ['cube_041_eigenstate_03110_spin_1.cube','cube_042_eigenstate_imag_03110_spin_1.cube','cube_043_eigenstate_03110_spin_2.cube','cube_044_eigenstate_imag_03110_spin_2.cube']
	fcubelist = ['cube_057_eigenstate_03114_spin_1.cube', 'cube_058_eigenstate_imag_03114_spin_1.cube', 'cube_059_eigenstate_03114_spin_2.cube', 'cube_060_eigenstate_imag_03114_spin_2.cube']


	tsta = time.time()
	#tint, tmo = get_trans_int_full_mpi(icubelist,fcubelist)
	tint, tmo = get_trans_int_full_mpi(icubelist,fcubelist,comm)
	tend = time.time()
	if rank == 0:
		print(tint,tmo,f'elapt: {tend-tsta:.3f}')

'''
	Expected Output:

	* Tansition Dipole Test
	Input state_i: ['cube_037_eigenstate_03109_spin_1.cube', 'cube_038_eigenstate_imag_03109_spin_1.cube', 'cube_039_eigenstate_03109_spin_2.cube', 'cube_040_eigenstate_imag_03109_spin_2.cube']
	Input state_f: ['cube_041_eigenstate_03110_spin_1.cube', 'cube_042_eigenstate_imag_03110_spin_1.cube', 'cube_043_eigenstate_03110_spin_2.cube', 'cube_044_eigenstate_imag_03110_spin_2.cube']
	* loading finished
	0  20  40  60  80 100 120 140 160 180 200 220 240 260Integral: 0.01452462996328659
	0.0 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-14.8405231 ,  -2.11590057,  22.06078192]))


	0  20  40  60  80 100 120 140 160 180 200 220 240 260Integral: 0.01452462996328659
	974.3991423880673 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-14.8405231 ,  -2.11590057,  22.06078192]))


serial version - correct
python Transition_ReIm_MPI.py 
* MPI - Tansition Dipole Test : nprocs: 1
0  50 100 150 200 250 974.3991423880673 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-14.8405231 ,  -2.11590057,  22.06078192])) elapt: 969.853


* MPI - Tansition Dipole Test : nprocs: 8
0   20 5408.971410469892 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-13.66778995,  -8.43602846,  -2.24228093])) elapt: 150.568

mpirun -np 8 python Transition_ReIm_MPI.py 
* MPI - Tansition Dipole Test : nprocs: 8
0 5408.971410469892 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-14.8405231 ,  -2.11590057,  22.06078192])) elapt: 151.009


mpirun -np 1 python Transition_ReIm_MPI.py 
* MPI - Tansition Dipole Test : nprocs: 1
0   20   40   60   80  100  120  140  160  180  200  220  240  260 974.3991423880673 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-13.66778995,  -8.43602846,  -2.24228093])) elapt: 988.018


# ------------- CORRECTED VALUES?

  NOTE !!! : Cannot use more than 8 procs on the head node : out of memory error!

### 3109 --> 3110
mpirun -np 1 python Transition_ReIm_MPI.py 
* MPI - Tansition Dipole Test : nprocs: 1
974.3991423880673 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-14.8405231 ,  -2.11590057,  22.06078192])) elapt: 967.859

### 3109 --> 3110
mpirun -np 8 python Transition_ReIm_MPI.py
* MPI - Tansition Dipole Test : nprocs: 8
974.3991423878336 (array([-13.66778995,  -8.43602846,  -2.24228093]), array([-14.8405231 ,  -2.11590057,  22.06078192])) elapt: 154.274

### 3104 --> 3114
* MPI - Tansition Dipole Test : nprocs: 8
939073.54229184 (array([ 642.26709371, -404.644395  ,  193.76769356]), array([ 460.99647552, -259.42558862,  213.22319452])) elapt: 151.528
* serial result for comparison
939073.542291989    (array([ 642.26709371, -404.644395  ,  193.76769356]), array([ 460.99647552, -259.42558862,  213.22319452]))


### 3104 --> 3114
* MPI - Tansition Dipole Test : nprocs: 64 - 1 node
939073.5422919724 (array([ 642.26709371, -404.644395  ,  193.76769356]), array([ 460.99647552, -259.42558862,  213.22319452])) elapt: 170.375
* MPI - Tansition Dipole Test : nprocs: 32 - 1 node
939073.5422919396 (array([ 642.26709371, -404.644395  ,  193.76769356]), array([ 460.99647552, -259.42558862,  213.22319452])) elapt: 197.763
* MPI - Tansition Dipole Test : nprocs: 32 - 4 node
939073.5422919849 (array([ 642.26709371, -404.644395  ,  193.76769356]), array([ 460.99647552, -259.42558862,  213.22319452])) elapt: 129.143

>> 1 node 32 best?
* MPI - Tansition Dipole Test : nprocs: 8
*loading finished*	939073.54229184 (array([ 642.26709371, -404.644395  ,  193.76769356]), array([ 460.99647552, -259.42558862,  213.22319452])) elapt: 152.596
'''


'''

 POSSIBLE BENCHMARKS
 * ---------------------------------------------
 * SOC-HOMO state cube files
 * ---------------------------------------------
['cube_001_eigenstate_03100_spin_1.cube', 'cube_002_eigenstate_imag_03100_spin_1.cube', 'cube_003_eigenstate_03100_spin_2.cube', 'cube_004_eigenstate_imag_03100_spin_2.cube']
['cube_005_eigenstate_03101_spin_1.cube', 'cube_006_eigenstate_imag_03101_spin_1.cube', 'cube_007_eigenstate_03101_spin_2.cube', 'cube_008_eigenstate_imag_03101_spin_2.cube']
['cube_009_eigenstate_03102_spin_1.cube', 'cube_010_eigenstate_imag_03102_spin_1.cube', 'cube_011_eigenstate_03102_spin_2.cube', 'cube_012_eigenstate_imag_03102_spin_2.cube']
['cube_013_eigenstate_03103_spin_1.cube', 'cube_014_eigenstate_imag_03103_spin_1.cube', 'cube_015_eigenstate_03103_spin_2.cube', 'cube_016_eigenstate_imag_03103_spin_2.cube']
['cube_017_eigenstate_03104_spin_1.cube', 'cube_018_eigenstate_imag_03104_spin_1.cube', 'cube_019_eigenstate_03104_spin_2.cube', 'cube_020_eigenstate_imag_03104_spin_2.cube']
['cube_021_eigenstate_03105_spin_1.cube', 'cube_022_eigenstate_imag_03105_spin_1.cube', 'cube_023_eigenstate_03105_spin_2.cube', 'cube_024_eigenstate_imag_03105_spin_2.cube']
['cube_025_eigenstate_03106_spin_1.cube', 'cube_026_eigenstate_imag_03106_spin_1.cube', 'cube_027_eigenstate_03106_spin_2.cube', 'cube_028_eigenstate_imag_03106_spin_2.cube']
['cube_029_eigenstate_03107_spin_1.cube', 'cube_030_eigenstate_imag_03107_spin_1.cube', 'cube_031_eigenstate_03107_spin_2.cube', 'cube_032_eigenstate_imag_03107_spin_2.cube']
['cube_033_eigenstate_03108_spin_1.cube', 'cube_034_eigenstate_imag_03108_spin_1.cube', 'cube_035_eigenstate_03108_spin_2.cube', 'cube_036_eigenstate_imag_03108_spin_2.cube']
['cube_037_eigenstate_03109_spin_1.cube', 'cube_038_eigenstate_imag_03109_spin_1.cube', 'cube_039_eigenstate_03109_spin_2.cube', 'cube_040_eigenstate_imag_03109_spin_2.cube']
 * ---------------------------------------------
 * SOC-LUMO state cube files
 * ---------------------------------------------
['cube_041_eigenstate_03110_spin_1.cube', 'cube_042_eigenstate_imag_03110_spin_1.cube', 'cube_043_eigenstate_03110_spin_2.cube', 'cube_044_eigenstate_imag_03110_spin_2.cube']
['cube_045_eigenstate_03111_spin_1.cube', 'cube_046_eigenstate_imag_03111_spin_1.cube', 'cube_047_eigenstate_03111_spin_2.cube', 'cube_048_eigenstate_imag_03111_spin_2.cube']
['cube_049_eigenstate_03112_spin_1.cube', 'cube_050_eigenstate_imag_03112_spin_1.cube', 'cube_051_eigenstate_03112_spin_2.cube', 'cube_052_eigenstate_imag_03112_spin_2.cube']
['cube_053_eigenstate_03113_spin_1.cube', 'cube_054_eigenstate_imag_03113_spin_1.cube', 'cube_055_eigenstate_03113_spin_2.cube', 'cube_056_eigenstate_imag_03113_spin_2.cube']
['cube_057_eigenstate_03114_spin_1.cube', 'cube_058_eigenstate_imag_03114_spin_1.cube', 'cube_059_eigenstate_03114_spin_2.cube', 'cube_060_eigenstate_imag_03114_spin_2.cube']
['cube_061_eigenstate_03115_spin_1.cube', 'cube_062_eigenstate_imag_03115_spin_1.cube', 'cube_063_eigenstate_03115_spin_2.cube', 'cube_064_eigenstate_imag_03115_spin_2.cube']
['cube_065_eigenstate_03116_spin_1.cube', 'cube_066_eigenstate_imag_03116_spin_1.cube', 'cube_067_eigenstate_03116_spin_2.cube', 'cube_068_eigenstate_imag_03116_spin_2.cube']
['cube_069_eigenstate_03117_spin_1.cube', 'cube_070_eigenstate_imag_03117_spin_1.cube', 'cube_071_eigenstate_03117_spin_2.cube', 'cube_072_eigenstate_imag_03117_spin_2.cube']
['cube_073_eigenstate_03118_spin_1.cube', 'cube_074_eigenstate_imag_03118_spin_1.cube', 'cube_075_eigenstate_03118_spin_2.cube', 'cube_076_eigenstate_imag_03118_spin_2.cube']
['cube_077_eigenstate_03119_spin_1.cube', 'cube_078_eigenstate_imag_03119_spin_1.cube', 'cube_079_eigenstate_03119_spin_2.cube', 'cube_080_eigenstate_imag_03119_spin_2.cube']


* ---------------------------------------------
* istate    soc_eval    fstate    soc_eval     transInt    transMoment
* ---------------------------------------------
3100   -6.777501      3110   -5.422019	278690.827702532	(array([-426.73186855,   -0.91900678,  -19.9012674 ]), array([-300.3769296 ,   50.47157911,  -58.48209054]))
3100   -6.777501      3111   -4.661404	 26767.929382436	(array([ 13.32261579, -32.17982608,  61.79167518]), array([ -74.36684528,  -15.02489065, -126.41404173]))
3100   -6.777501      3112   -4.600147	 68597.924863521	(array([-155.20297133,   54.67814594,   75.08293288]), array([ -13.87075126, -176.66200427,   66.93993283]))
3100   -6.777501      3113   -4.249339	  7049.637247360	(array([49.95463146, 41.46292027, -5.92386451]), array([-11.6798706 , -46.03614929,  23.32723078]))
3100   -6.777501      3114   -4.215337	141107.885769785	(array([-260.57990167,  229.57870208,    9.48550725]), array([-106.15941016,   50.61507117,   81.10449756]))
3100   -6.777501      3115   -3.805426	 13177.478584726	(array([ -2.55992452, -37.12839761, -64.93260545]), array([-39.55132018, -26.61370769,  72.82559884]))
3100   -6.777501      3116   -3.792119	209922.204528308	(array([  7.75047723,   0.37974566, -29.169301  ]), array([-144.32316653,   23.35693459,  433.17019694]))
3100   -6.777501      3117   -3.735065	 44173.250003567	(array([-76.25793021, -35.01560326, 179.06808731]), array([-6.62606425e+01,  2.33387361e-02,  2.60006237e+01]))
3100   -6.777501      3118   -3.705549	195319.324332637	(array([-172.05866439, -114.63138363, -228.26361991]), array([-27.97905834,  69.05372512, 308.08969699]))
3100   -6.777501      3119   -3.195316	 11312.142002575	(array([-42.67851087, -59.95115343, -15.46003262]), array([25.82208201, 63.11592594, 31.73536323]))
3101   -6.744122      3110   -5.422019	 31012.660572504	(array([-1.50818457e+01, -1.71509115e+02, -7.62056776e-02]), array([30.9940869 ,  7.28494536, 18.87093639]))
3101   -6.744122      3111   -4.661404	 20917.243137637	(array([-1.15228845, -0.87400564, 25.42827801]), array([ -96.68563247,   -5.42141875, -104.36019765]))
3101   -6.744122      3112   -4.600147	 72195.367058513	(array([137.77248461,  41.21027786, 224.11509733]), array([ 11.25240984, -11.98319578, -31.90661341]))
3101   -6.744122      3113   -4.249339	 42480.963532743	(array([-152.53278778,   28.73198426,    3.5589523 ]), array([-48.36341141, -84.43486571,  94.38354206]))
3101   -6.744122      3114   -4.215337	 28100.409534208	(array([ 92.14280412, -78.61351855,  52.91082092]), array([-11.70971273,  91.43417248, -46.18601137]))
3101   -6.744122      3115   -3.805426	 61969.063057436	(array([-12.911801  ,   0.7385402 , -73.00214893]), array([219.67553155, -61.52874276, -66.55346658]))
3101   -6.744122      3116   -3.792119	 16484.676217550	(array([-28.23920795,  15.5858775 , -27.02537801]), array([ 46.84542435, -78.20304994, -80.02325859]))
3101   -6.744122      3117   -3.735065	 64748.506476027	(array([  3.60341068,  41.27392791, 117.42425887]), array([-70.75259656, 112.2418849 , 177.8745557 ]))
3101   -6.744122      3118   -3.705549	 17630.900758745	(array([  2.17196971,  39.33472176, -29.1877709 ]), array([-123.2694009 ,    5.31518737,   -1.85488147]))
3101   -6.744122      3119   -3.195316	108223.311256772	(array([-138.18809345, -230.62044171, -120.1518911 ]), array([ 18.59023948, 120.36266277,  81.68432791]))
3102   -6.731431      3110   -5.422019	 48197.243524054	(array([  -1.50078796,  108.71607852, -102.09132281]), array([118.88733481,  96.18861839,  50.66279257]))
3102   -6.731431      3111   -4.661404	 66431.559270674	(array([ 70.3615791 , -34.93779779,  18.35677202]), array([154.92378947,  62.60559714, 178.89199347]))
3102   -6.731431      3112   -4.600147	 45065.492308359	(array([114.04728701, -30.22536932, 144.48508422]), array([ 29.8990548 , -27.01737039, -92.98012875]))
3102   -6.731431      3113   -4.249339	 45153.845476482	(array([-139.46998069,   82.72829109,  -50.34247891]), array([-50.05266611, 108.25611027, -45.81462472]))
3102   -6.731431      3114   -4.215337	 39980.661935279	(array([-138.30064277,    0.9827816 ,   61.8161862 ]), array([104.83342986,  22.16208868, -74.49953838]))
3102   -6.731431      3115   -3.805426	 17339.180646526	(array([ 35.13478752, -96.12212172, -15.27890085]), array([-16.37005435, -29.81779466, -73.99149072]))
3102   -6.731431      3116   -3.792119	104641.252241287	(array([-253.74593519,   51.48500802,  159.37848341]), array([-72.32316574,  -9.33742426,  82.97118655]))
3102   -6.731431      3117   -3.735065	 40703.529290500	(array([42.83740242, 50.30270792, 46.4043341 ]), array([184.70743383,   0.35884323,   8.23387622]))
3102   -6.731431      3118   -3.705549	143817.380388288	(array([-38.71418445,  39.7202397 ,  94.82411563]), array([  5.76307407, 164.96184662, 323.27025552]))
3102   -6.731431      3119   -3.195316	  6183.814022208	(array([-17.39645674,  -0.57972748,  26.21544068]), array([-58.74831935, -40.61037069,   9.64492961]))
3103   -6.681749      3110   -5.422019	  4352.889220549	(array([ 25.86216681, -46.0580456 ,  14.80765386]), array([ 13.23839711,  28.39350547, -19.02579984]))
3103   -6.681749      3111   -4.661404	 42425.179920727	(array([  35.11016282,  -84.10319128, -109.10974648]), array([ -14.18676537,  102.93516926, -106.85157671]))
3103   -6.681749      3112   -4.600147	 43187.941095615	(array([170.9735539 ,  57.87660234,  68.57620802]), array([-28.33071406, -69.78458822, -15.2009685 ]))
3103   -6.681749      3113   -4.249339	728422.496331176	(array([ 274.69539852, -154.49209184,  173.80576566]), array([ 638.58740121, -388.79237878,  199.83818695]))
3103   -6.681749      3114   -4.215337	 15877.920674847	(array([-82.37051118,  -7.52267345, -73.57743623]), array([-16.36605484,  44.41502024, -37.17859668]))
3103   -6.681749      3115   -3.805426	269467.402993028	(array([ -16.11495722, -116.02274846,   21.73325049]), array([303.38404787, -15.55779014, 403.72041498]))
3103   -6.681749      3116   -3.792119	 19426.584482648	(array([ 72.47794649, -36.88558281, -72.89196384]), array([-57.39952697, -59.51703154,  25.74421106]))
3103   -6.681749      3117   -3.735065	 81247.228566705	(array([ 43.20492275, 109.24278239, 108.75339674]), array([ 163.61278041, -143.91272842,  -90.21785352]))
3103   -6.681749      3118   -3.705549	 39483.005285729	(array([   1.54447567,   50.47047348, -117.11955934]), array([-146.91731889,   -0.59534612,  -40.38944144]))
3103   -6.681749      3119   -3.195316	 94788.454415873	(array([ -66.18109647, -263.36159608,  -47.00163628]), array([-131.5538256 ,   33.37863627,   20.48146458]))
3104   -6.648448      3110   -5.422019	469180.510813900	(array([ 338.41298733, -327.42063146,   22.31749612]), array([-218.4302516 , -429.17980754, -122.66922297]))
3104   -6.648448      3111   -4.661404	 79458.289125383	(array([-232.34666084,  -88.02754754,  -82.20941354]), array([ 34.70952302, -90.69304869, -39.19313015]))
3104   -6.648448      3112   -4.600147	 53382.608318263	(array([ -0.91225133, -67.24250928, -65.04935725]), array([ 14.31812739, -10.50071163, 210.50778719]))
3104   -6.648448      3113   -4.249339	 30676.739178368	(array([-10.78597817, -61.30046705,  22.48722489]), array([110.22588808, -34.55310453, 113.81263495]))
3104   -6.648448      3114   -4.215337	939073.542291989	(array([ 642.26709371, -404.644395  ,  193.76769356]), array([ 460.99647552, -259.42558862,  213.22319452]))
3104   -6.648448      3115   -3.805426	 21815.213400720	(array([-54.69190595,  81.56718064,  54.32102437]), array([ 13.96210618, -38.252801  ,  86.9586855 ]))
3104   -6.648448      3116   -3.792119	325745.725141847	(array([ 93.55408141, -48.20562094, 121.45984559]), array([-206.1069066 ,   15.44017904, -507.14753961]))
3104   -6.648448      3117   -3.735065	 78355.229440060	(array([-176.72007642,   34.78825598, -184.1720252 ]), array([ 57.38053625,  75.13017146, -55.30477201]))
'''
