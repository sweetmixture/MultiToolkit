import sys
from ase.io import read

# Replace 'your_file.cif' with the path to your CIF file
cif_file = sys.argv[1]

# Read the CIF file
structure = read(cif_file)

# Access the lattice vectors
lattice_vectors = structure.get_cell()

# Access the atomic positions (in fractional coordinates)
fractional_coordinates = structure.get_scaled_positions()


# ------------------------------------------------------------------------
# print lattice vectors in FHIAIMS format
# ------------------------------------------------------------------------


for lvec in lattice_vectors:

    print(f'lattice_vector {lvec[0]:12.6f}{lvec[1]:12.6f}{lvec[2]:12.6f}')

for elem,frac in zip(structure,fractional_coordinates):

    print(f'atom_frac {frac[0]:20.12f}{frac[1]:20.12f}{frac[2]:20.12f} {elem.symbol:4s}')
