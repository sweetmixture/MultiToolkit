#!/bin/python


import sys,os
from Extractor.GULPstruct import GULPLattice


# using no smearing

# require only input file !! -> filepath
cwd = os.getcwd()
filepath = os.path.join(cwd,sys.argv[1])
print(filepath)

glattice = GULPLattice()
glattice.set_lattice(filepath)		# path - standard output file


pairlist = []
pair = ['S','S']
pairlist.append(pair)
pair = ['S','Li']
pairlist.append(pair)
pair = ['S','Fe']
pairlist.append(pair)
pair = ['Li','Li']
pairlist.append(pair)
pair = ['Li','Fe']
pairlist.append(pair)
pair = ['Fe','Fe']
pairlist.append(pair)
#---

'''
	Description
	
	* total 6 pairs

		(1) S  S
		(2) S  Li
		(3) S  Fe
		(4) Li Li
		(5) Li Fe
		(6) Fe Fe

'''


rlist = []
rdflist = []

for pair in pairlist:

	'''
		case size = 0 / case size = 24

		* size = 0
			Mn Mn
			Li Li (x)
			Tc Tc (x)

			Mn Li (x)
			Mn Tc (x)
			Li Tc (x)

		* size = 24
			Mn Mn (x)
			Li Li
			Tc Tc

			Mn Li (x)
			Mn Tc (x)
			Li Tc

	'''
			
	#
	# get 'rdf'
	#
	r, rdf = glattice.get_rdf(pair=pair,gaussian=True,smearing=0.020)
	#r, rdf = glattice.get_rdf(pair=pair)
	
	rlist.append(r)
	rdflist.append(rdf)
	print(len(r))

with open('output.rdf','w') as f:

	for x in range(len(rlist[0])):

		f.write('%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n' %
				(rlist[0][x],rdflist[0][x],
				 rlist[1][x],rdflist[1][x],
				 rlist[2][x],rdflist[2][x],
				 rlist[3][x],rdflist[3][x],
				 rlist[4][x],rdflist[4][x],
				 rlist[5][x],rdflist[5][x]))

sys.exit(1)

#glattice.reset()
#glattice.set_lattice(sys.argv[2])
