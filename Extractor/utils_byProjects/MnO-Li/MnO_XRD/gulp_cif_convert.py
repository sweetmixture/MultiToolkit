#!/bin/python

'''
	Xingfan Zhang, 12/2023
	Woongkyu Jee, 12/203
'''

import os
import sys
from tqdm import tqdm

def extract_key_sections(content):
	sections = {
		"header": [],
		"chemical_info": [],
		"cell_info": [],
		"symmetry": [],
		"atom_site": []
	}
	
	current_section = "header"
	for line in content:
		if "_chemical_name_common" in line:
			current_section = "chemical_info"
		elif "_cell_length_a" in line:
			current_section = "cell_info"
		elif "_symmetry_equiv_pos_site_id" in line:
			current_section = "symmetry"
		elif "_atom_site_type_symbol" in line:
			current_section = "atom_site"
		
		sections[current_section].append(line.strip())
	
		# modification 'Tc' -> 'Mn' for this research purpose
		#if 'Tc' in line:
		#	 line = line.replace('Tc','Mn')

	return sections

def transform_cif_to_standard(input_content):
	sections = extract_key_sections(input_content)
	
	standard_header = [
		"",
		"#======================================================================",
		"# CRYSTAL DATA",
		"#----------------------------------------------------------------------",
		"data_VESTA_phase_1",
		""
	]
	
	standard_chemical_info = sections["chemical_info"] + [""]
	standard_cell_info = sections["cell_info"] + [""]
	standard_atom_site = sections["atom_site"] + [""]
	
	transformed_content = (standard_header + standard_chemical_info + 
						   standard_cell_info + standard_atom_site)
	
	return transformed_content


# Find all files that match the pattern A*/cryst.cif in the current directory
files_to_transform = [os.path.join(root, filename) 
					  for root, dirs, files in os.walk(".")
					  for filename in files 
					  if filename == "cryst.cif" and root.startswith("./A")]

total_files = len(files_to_transform)
print(f"Found {total_files} files to transform.")

# Transform each file and save as b.cif in the same directory
#for idx, file_path in enumerate(files_to_transform, start=1):
for idx, file_path in tqdm(enumerate(files_to_transform, start=1), total=len(files_to_transform), desc="Converting CIF"):
	with open(file_path, "r") as file_a:
		#content_a = file_a.readlines()

		'''
			custom .. wkjee 31.01.2024
			for the LiMnO2 project purpose ... replace dummy reduced Mn (Tc) -> Mn
		'''
		content_a = [line.replace('Tc', 'Mn') for line in file_a.readlines()]

	transformed_a = transform_cif_to_standard(content_a)

	output_path = os.path.join(os.path.dirname(file_path), "std.cif")
	with open(output_path, "w") as file_b:
		file_b.write("\n".join(transformed_a))
	
	# Print progress
	#print(f"Transformed {idx}/{total_files} files. Current: {file_path}")

print("Transformation complete!")
