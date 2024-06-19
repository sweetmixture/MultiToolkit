from pymatgen.core import Structure
from pymatgen.io.cif import CifParser, CifWriter
import sys

# Load the CIF file
cif_file_path = '/work/e05/e05/wkjee/SolidSolution/Batteries/LiS/tfklmc_10_t1/result/std.cif'
parser = CifParser(cif_file_path)

#
# structure information !
#
structure = parser.get_structures()[0]

# Print lattice vectors
lattice = structure.lattice
print("Lattice vectors (in Å):")
print(f"a: {lattice.a}, b: {lattice.b}, c: {lattice.c}")
print(f"a vector: {lattice.matrix[0]}")
print(f"b vector: {lattice.matrix[1]}")
print(f"c vector: {lattice.matrix[2]}")

# Print lattice angles
print("\nLattice angles (in degrees):")
print(f"alpha: {lattice.alpha}, beta: {lattice.beta}, gamma: {lattice.gamma}")

# Print lattice parameters
print("\nLattice parameters (in Å and degrees):")
print(f"a: {lattice.a}, b: {lattice.b}, c: {lattice.c}")
print(f"alpha: {lattice.alpha}, beta: {lattice.beta}, gamma: {lattice.gamma}")

# Print fractional coordinates of atoms with their element names
print("\nFractional coordinates of atoms:")
for site in structure:
	print(f"Element: {site.specie}, Fractional Coords: {site.frac_coords}")


# write back to different name
cifwriter = CifWriter(structure)
cifwriter.write_file('new_cif.cif')





# Example usage
#if __name__ == "__main__":
#	cif_file_path = '/work/e05/e05/wkjee/SolidSolution/Batteries/LiS/tfklmc_10_t1/result/A0/cryst.cif'  # Replace with your CIF file path
#	print_structure_info(cif_file_path)
#
