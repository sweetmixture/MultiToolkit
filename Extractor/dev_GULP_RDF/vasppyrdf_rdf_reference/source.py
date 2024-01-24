# Create a pymatgen Structure for NaCl
from pymatgen.core import Structure, Lattice

a = 5.6402 # NaCl lattice parameter
lattice = Lattice.from_parameters(a, a, a, 90.0, 90.0, 90.0)



structure = Structure.from_spacegroup(sg='Fm-3m', lattice=lattice,
                          species=['Na', 'Cl'],
                          coords=[[0,0,0], [0.5, 0, 0]])

from vasppy.rdf import RadialDistributionFunction

indices_na = [i for i, site in enumerate(structure) if site.species_string == 'Na']
indices_cl = [i for i, site in enumerate(structure) if site.species_string == 'Cl']
print(indices_na)
print(indices_cl)


rdf_nana = RadialDistributionFunction(structures=[structure],
                                      indices_i=indices_na)
rdf_clcl = RadialDistributionFunction(structures=[structure],
                                      indices_i=indices_cl)

rdf_nacl = RadialDistributionFunction(structures=[structure],
                                      indices_i=indices_na, indices_j=indices_cl)

#access  data
#print(rdf_nana.r)
#print(rdf_nana.rdf)

#for r,rdf in zip(rdf_nana.r,rdf_nana.rdf):
#	print(r,rdf)

print(len(rdf_nana.r),len(rdf_clcl.r),len(rdf_nacl.r))

for i in range(len(rdf_nana.r)):

	print('%.6f\t%.6f\t%.6f\t%.6f' % (rdf_nana.r[i],rdf_nana.rdf[i],rdf_nacl.rdf[i],rdf_clcl.rdf[i]))
