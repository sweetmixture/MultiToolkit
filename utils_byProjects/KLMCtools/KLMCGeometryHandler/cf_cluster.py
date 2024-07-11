#
# 07.2024 W.JEE
#
# Taking two geometry (assuming in same atom order)
# calculate rmsd 
#
from KLMCGeometryHandler import KLMCGeometryHandler
import sys
import numpy as np

file1 = sys.argv[1]
file2 = sys.argv[2]

print(file1,file2)

struct1 = KLMCGeometryHandler(file1)
struct2 = KLMCGeometryHandler(file2)


elem1, cart1 = struct1.get_cart()
elem2, cart2 = struct2.get_cart()

#print(elem1,cart1)
#print(elem2,cart2)

total_n = len(elem1)

#for a,b in zip(elem1,elem2):
#	print(a,b)

rmsd = 0.

for c1, c2 in zip(cart1, cart2):

	c1 = np.array(c1)
	c2 = np.array(c2)

	dr = c2 - c1
	dr_sqr = np.linalg.norm(dr) ** 2.
	rmsd += dr_sqr

	print(f'{dr[0]:20.12f}{dr[1]:20.12f}{dr[2]:20.12f}')

print(f'rmsd : {rmsd/total_n:20.12f}')
