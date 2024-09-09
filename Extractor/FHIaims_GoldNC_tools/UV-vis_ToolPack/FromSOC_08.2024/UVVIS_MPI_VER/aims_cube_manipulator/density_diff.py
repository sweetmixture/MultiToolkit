#
# WKJEE 08.2024 Au25 Project
#

#
# get transition_density = final_density - initial_density
#

from ase.io.cube import read_cube, write_cube
import numpy as np
import sys

_ista = 'dens_' + sys.argv[1] + '.cube'
_fsta = 'dens_' + sys.argv[2] + '.cube'

print(_ista,_fsta)

icube = read_cube(open(_ista))
fcube = read_cube(open(_fsta))

dcube = fcube['data'] - icube['data']

f = f'delta_{sys.argv[1]}_{sys.argv[2]}.cube'

write_cube(open(f,'w'),icube['atoms'],data=dcube,origin=icube['origin'])
