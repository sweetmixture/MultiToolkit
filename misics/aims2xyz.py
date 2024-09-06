#
# WKJEE 09.2024
#

import sys,os

_f = sys.argv[1]
_n = 0

specieslist = []
xyzlist = []

with open(_f,'r') as f:

	for line in f:

		if 'atom' in line:
			_n += 1

			l = line.strip().split()

			xyz = [ float(item) for item in l[1:4] ]
			
			species = l[-1]

			specieslist.append(species)
			xyzlist.append(xyz)


print(_n)
print('aims2xyz')
for species, xyz in zip(specieslist,xyzlist):
	print(f'{species:>3s}{xyz[0]:12.6f}{xyz[1]:12.6f}{xyz[2]:12.6f}')

			
