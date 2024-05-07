import sys
from ase.io.cube import read_cube, write_cube
# from ase.io.cube import read_cube_data

# Path to the Gaussian cube file
_cubefile = '/work/e05/e05/wkjee/Gold/cubes1/cubes/spin_down_0_HOMO.cube'

#
# Open the cube file and read it using read_cube function
#
with open(_cubefile, 'r') as fileobj:
	cube_obj = read_cube(fileobj,read_data=True,verbose=True)
	print(f' ! keys')
	print(cube_obj.keys())
#
# Possible Output
# dict_keys(['atoms', 'data', 'origin', 'spacing', 'labels', 'datas'])
#
'''
	* 'atoms': Atoms object
	* 'data' : (Nx, Ny, Nz) ndarray
	* 'origin': (3,) ndarray, specifying the cube_data origin.
	* 'spacing': (3, 3) ndarray, representing voxel size
'''
atoms = cube_obj['atoms']
data  = cube_obj['data']
origin = cube_obj['origin']
spacing = cube_obj['spacing']

grid = cube_obj['data'].shape
nx_max = grid[0]
ny_max = grid[1]
nz_max = grid[2]

print(f' * grid info')
#print(grid,type(grid))
print(nx_max,ny_max,nz_max)
print(f' * origin info (Å)')
print(origin)
print(f' * spacing info (Å)')
print(spacing)

##
## looping grid
##
def get_density(data,spacing,grid):
	nx,ny,nz = grid
	r = spacing[0]*nx + spacing[1]*ny + spacing[2]*nz
	return r, data[nx,ny,nz]

print(f'density')
g = (0,79,127)
print(get_density(data,spacing,g))
print('end')
# 0  79 127
print(data[0][79][129])

for nx in range(nx_max):
	for ny in range(ny_max):
		for nz in range(nz_max):
			g = (nx,ny,nz)

			r,dens = get_density(data,spacing,g)
			if dens != 0:
				print(f'{nx:4d}{ny:4d}{nz:4d} {r[0]:12.8f}{r[1]:12.8f}{r[2]:12.8f} : {dens:12.8e}')
				sys.exit()


# ----
#data, atoms = read_cube_data(_cubefile) #,format='cube',read_data=True,full_output=True)
#print(atoms.get_positions())
#print(atoms.get_cell())
# ----

# output check
_set_out = False
_outcube = 'out.cube'
if _set_out:
	with open(_outcube,'w') as f:
		write_cube(f, atoms, data=data, origin=origin, comment=None)

