#
#   03.2024 W.Jee 
#
#   KLMC Solid Solution: scripts for production phase
#
# ----------------------------------------------------------
#
#   * this script is for generating radial distribution function for desired pairs (user's choice).
#     (only for a single gulp periodic standard output file)
#
#   * setting desired pairs to investigate is user's responsibility.
#     user must set '_pairlist' variable below
#
#     in this example, using a few possible pairs in LiMnO2 where Tc represents reduced Mn: see line 19
#
# USER DEFINE variables ----
_filepath = 'gulp_klmc.gout'     # set gulp output file that you want to generate RDF
_smearing_factor = 0.02          # set gaussian smearing, or broadening factor for RDF peaks
_pairlist = [['Mn','Mn'], ['Li','Li'], ['Tc','Tc'], ['Mn','Li'], ['Mn','Tc'], ['Li','Tc']]    # example of pairs in LiMnO2
_output_rdf_filename = 'output.rdf'
#   
#   * printed result for the given example in this script will look like ... (in column format)
#     r  MnMn  r  LiLi  r  TcTc  r  MnLi  r  MnTc  r  LiTc
#
#   also lines 92 ~ 104 should be modifed for the pairs you want to print !!!
#   
# USER DEFINE ----

import sys,os
from Extractor.GULPstruct import GULPLattice

cwd = os.getcwd()
filepath = os.path.join(cwd,_filepath)
pairlist = _pairlist

glattice = GULPLattice()
glattice.set_lattice(filepath)		# path - standard output file

print('check 1')
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
			
	print('check 2')
	#
	# get 'rdf'
	#
	r, rdf = glattice.get_rdf(pair=pair,gaussian=True,smearing=_smearing_factor)
	#r, rdf = glattice.get_rdf(pair=pair)
	
	rlist.append(r)
	rdflist.append(rdf)
	#print(len(r))


# USER DEFINE ----
with open(f'{_output_rdf_filename}','w') as f:

	for x in range(len(rlist[0])):

		f.write('%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n' %
				(rlist[0][x],rdflist[0][x],
				 rlist[1][x],rdflist[1][x],
				 rlist[2][x],rdflist[2][x],
				 rlist[3][x],rdflist[3][x],
				 rlist[4][x],rdflist[4][x],
				 rlist[5][x],rdflist[5][x]))
# USER DEFINE ----


sys.exit(1)

#glattice.reset()
#glattice.set_lattice(sys.argv[2])
