from ase import Atoms
from ase.io import read, write
import numpy as np
import random

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
def check_for_collisions(new_structure, current_structure, min_distance=2.0):
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

# Function to attach L-Cystine to gold-sulfur cluster with retries from scratch on failure
def attach_l_cystine_with_retries():
    """Attempt to attach L-Cystine molecules to each sulfur atom in the gold cluster.
    If any failure occurs, the process starts over from the beginning."""
    
    # Loop until the attachment succeeds for all sulfur atoms
    while True:
        print("Starting the process...")

        # Read the gold-sulfur cluster and the L-Cystine molecule
        gold_sulfur_cluster = read('ja801173r-file005-Au25-S18-new.xyz')
        l_cystine = read('L-Cystine.xyz')

        # Identify sulfur atoms in the gold-sulfur cluster
        sulfur_indices = [atom.index for atom in gold_sulfur_cluster if atom.symbol == 'S']

        # Initialize an empty list to store the modified structure
        full_structure = gold_sulfur_cluster.copy()

        # To avoid re-adding the sulfur atoms later, remove them from the gold-sulfur cluster
        full_structure = full_structure[[atom.index for atom in full_structure if atom.index not in sulfur_indices]]

        # Keep track of success status
        successfully_attached_all = True

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

            # Try random rotations until there is no collision
            attempts = 0
            max_rotation_attempts = 50  # Limit attempts per sulfur atom for one full try
            while True:
                attempts += 1
                # Check for collisions before adding the translated L-Cystine to the structure
                if not check_for_collisions(l_cystine_translated, full_structure):
                    # No collision detected, so add the translated L-Cystine to the full structure
                    full_structure += l_cystine_translated
                    print(f"Successfully attached L-Cystine at sulfur atom index {si}.")
                    break  # Move on to the next sulfur atom

                if attempts > max_rotation_attempts:
                    # Too many attempts, restart the entire process
                    print(f"Failed to find a valid orientation for sulfur atom at index {si}. Restarting the process...")
                    successfully_attached_all = False
                    break

                # Apply a random rotation to attempt a different orientation
                l_cystine_translated = random_rotation(l_cystine_translated, sulfur_pos)
                print(f"Collision detected for sulfur atom index {si}. Retrying...")

            # If any sulfur attachment fails, break out of the main loop and retry
            if not successfully_attached_all:
                break

        if successfully_attached_all:
            print("All L-Cystine molecules successfully attached. Saving structure...")
            write('Au25-SCystine18.xyz', full_structure)
            print("Modified structure saved as 'Au25-S18-Cystine_replaced_no_collisions_random_rotations_retry_until_success.xyz'")
            break  # Exit the infinite loop if all molecules were successfully attached


# Run the process
attach_l_cystine_with_retries()

