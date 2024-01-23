#!/bin/python


import sys,os
from Extractor.GULPstruct import GULPLattice


# using no smearing

cwd = os.getcwd()
filepath = os.path.join(cwd,sys.argv[1])
print(filepath)

glattice = GULPLattice()
glattice.set_lattice(filepath)		# path - standard output file


pairlist = []
pair = ['Mn','Mn']
pairlist.append(pair)
pair = ['Li','Li']
pairlist.append(pair)
pair = ['Tc','Tc']
pairlist.append(pair)

pair = ['Mn','Li']
pairlist.append(pair)
pair = ['Mn','Tc']
pairlist.append(pair)
pair = ['Li','Tc']
pairlist.append(pair)

'''
	* total 6 pairs

		(1) Mn Mn			(0,1)
		(2) Li Li	3,4		(2,3)
		(3) Tc Tc	5,6		(4,5)

		(4) Mn Li	7,8		(6,7)
		(5) Mn Tc	9,10	(8,9)
		(6) Li Tc	11,12	(10,11)
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
