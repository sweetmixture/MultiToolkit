from ase import Atoms
from ase.io import read, write
import numpy as np
import random

# Read the gold-sulfur cluster and the L-Cystine molecule
gold_sulfur_cluster = read('ja801173r-file005-Au25-S18-new.xyz')
l_cystine = read('L-Cystine.xyz')

# Identify sulfur atoms in the gold-sulfur cluster
sulfur_indices = [atom.index for atom in gold_sulfur_cluster if atom.symbol == 'S']

# Initialize an empty list to store the modified structure
full_structure = gold_sulfur_cluster.copy()

# To avoid re-adding the sulfur atoms later, remove them from the gold-sulfur cluster
full_structure = full_structure[[atom.index for atom in full_structure if atom.index not in sulfur_indices]]

# Function to remove H atoms near sulfur atoms in L-Cystine
def remove_nearest_hydrogen(l_cystine_structure, bond_length_tolerance=1.4):
    """Remove the nearest hydrogen atom bonded to sulfur in the L-Cystine structure."""
    new_l_cystine = l_cystine_structure.copy()

    # Find the index of the sulfur atom in L-Cystine
    sulfur_index = [atom.index for atom in new_l_cystine if atom.symbol == 'S'][0]
    
    # Find the hydrogen atoms
    hydrogens = [atom.index for atom in new_l_cystine if atom.symbol == 'H']
    
    # Identify the closest hydrogen to the sulfur atom
    closest_hydrogen = None
    closest_distance = float('inf')

    for h_index in hydrogens:
        distance = new_l_cystine.get_distance(sulfur_index, h_index)
        if distance < closest_distance and distance < bond_length_tolerance:
            closest_distance = distance
            closest_hydrogen = h_index
    
    # If a close hydrogen atom is found, remove it
    if closest_hydrogen is not None:
        new_l_cystine.pop(closest_hydrogen)
    
    return new_l_cystine

# Function to check if any atoms are too close (collisions)
def check_for_collisions(new_structure, current_structure, min_distance=1.8):
    """Check if atoms in the new structure are too close to atoms in the current structure."""
    for atom in new_structure:
        for existing_atom in current_structure:
            distance = np.linalg.norm(new_structure.positions[atom.index] - current_structure.positions[existing_atom.index])
            if distance < min_distance:
                return True  # Collision detected
    return False  # No collision

# Function to apply random rotations to the L-Cystine molecule around a random axis
def random_rotation(l_cystine_structure, center_of_rotation, max_rotation_angle=360):
    """Apply a random rotation to the L-Cystine molecule."""
    rotated_l_cystine = l_cystine_structure.copy()

    # Generate a random unit vector as the rotation axis
    random_axis = np.random.normal(size=3)
    random_axis /= np.linalg.norm(random_axis)  # Normalize to make it a unit vector

    # Generate a random rotation angle between 0 and max_rotation_angle degrees
    random_angle = random.uniform(0, max_rotation_angle)

    # Rotate around the random axis with a random angle
    rotated_l_cystine.rotate(v=random_axis, a=random_angle, center=center_of_rotation)
    
    return rotated_l_cystine

# Attach the L-Cystine molecule to each S atom's position, ensuring no collisions
for si in sulfur_indices:
    # Get the position of the sulfur atom in the gold cluster
    sulfur_pos = gold_sulfur_cluster.positions[si]

    # Remove the nearest hydrogen atom from the L-Cystine molecule
    l_cystine_modified = remove_nearest_hydrogen(l_cystine)

    # Translate the modified L-Cystine so that its sulfur atom matches the sulfur position in the cluster
    cystine_sulfur_pos = l_cystine_modified.positions[l_cystine_modified.get_chemical_symbols().index('S')]
    translation_vector = sulfur_pos - cystine_sulfur_pos
    l_cystine_translated = l_cystine_modified.copy()
    l_cystine_translated.translate(translation_vector)

    # Attempt to attach the L-Cystine with random orientations if a collision is detected
    max_rotation_attempts = 50  # Try up to 50 random orientations

    # Initialize successful attachment flag
    successfully_attached = False

    for attempt in range(max_rotation_attempts):
        # Check for collisions before adding the translated L-Cystine to the structure
        if not check_for_collisions(l_cystine_translated, full_structure):
            # No collision detected, so add the translated L-Cystine to the full structure
            full_structure += l_cystine_translated
            successfully_attached = True
            break
        else:
            # Apply a random rotation to attempt a different orientation
            l_cystine_translated = random_rotation(l_cystine_translated, sulfur_pos)
    
    if not successfully_attached:
        print(f"Unable to find a valid orientation for sulfur atom at index {si} after {max_rotation_attempts} attempts.")

# Save the combined structure to a new XYZ file
write('Au25-S18-LCystine_Added.xyz', full_structure)
print("Modified structure saved as 'Au25-S18-Cystine_replaced_no_collisions_random_rotations.xyz'")

