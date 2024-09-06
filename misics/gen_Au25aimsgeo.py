#
# WKJEE 09.2024
#

import sys,os

_file = sys.argv[1]

corr='initial_moment 0.04'

with open(_file,'r') as f:

	f.readline()
	f.readline()
	for line in f:

		ls = line.strip().split()

		species = ls[0]
		xyz = ls[1:]
		xyz = [ float(item) for item in xyz ]

		print(f'atom {xyz[0]:12.6f}{xyz[1]:12.6f}{xyz[2]:12.6f}{species:>4s}')
		if species == 'Au':
			print(corr)
