import numpy as np
from mpi4py import MPI
import time

grid = (267, 246, 236)
#grid = (2670, 246, 236)
total_points = grid[0] * grid[1] * grid[2]
#grid = (2, 3, 4)

#for nx in range(grid[0]):
#	for ny in range(grid[1]):
#		for nz in range(grid[2]):
#			print(nx,ny,nz)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
	print(f'psize : {size}')
tsta = time.time()

# Divide the workload among processes
points_per_process = total_points // size
remainder = total_points % size

#
# Block-Distribution
# Determine the start and end indices for each process
if rank < remainder:
    start_index = rank * (points_per_process + 1)
    end_index = start_index + points_per_process + 1
else:
    start_index = rank * points_per_process + remainder
    end_index = start_index + points_per_process

local_res = np.array([0.,0.,0.])
#for index in range(total_points):
for index in range(start_index, end_index):
	nx = index // (grid[1] * grid[2])
	ny = (index // grid[2]) % grid[1]
	nz = index % grid[2]
	#local_res += (nx + ny + nz)
	local_res += np.array([nx,0.,0.]) + np.array([0.,ny,0.]) + np.array([0.,0.,nz])
	#print(nx, ny, nz)

# Reduce all partial sums to the root process
res = comm.reduce(local_res, op=MPI.SUM, root=0)

tend = time.time()

if rank == 0:
	print(f'elapsed time : {tend-tsta:.4f} s')
	print(f'result : {res}, {np.sum(res)}')
	print(f'task size : {total_points}')

'''
	Possible Output
'''
