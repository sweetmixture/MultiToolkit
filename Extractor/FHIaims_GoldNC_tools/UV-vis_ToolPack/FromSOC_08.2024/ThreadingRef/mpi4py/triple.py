import numpy as np
import mpi4py
import time


grid = (267, 246, 236)
grid = (2670, 246, 236)
#grid = (2, 3, 4)

#for nx in range(grid[0]):
#	for ny in range(grid[1]):
#		for nz in range(grid[2]):
#			print(nx,ny,nz)

tsta = time.time()

res = 0
total_points = grid[0] * grid[1] * grid[2]
for index in range(total_points):
	nx = index // (grid[1] * grid[2])
	ny = (index // grid[2]) % grid[1]
	nz = index % grid[2]
	res += (nx + ny + nz)
	#print(nx, ny, nz)

tend = time.time()

print(f'elapsed time : {tend-tsta:.4f} s')
print(f'result : {res}')
print(f'task size : {total_points}')
'''
python triple.py 
elapsed time : 5.4480 s
python triple.py 
elapsed time : 5.6611 s
result : 5781855096

MPI:
elapsed time : 4.9767 s
result : 5781855096
'''
