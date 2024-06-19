#!/bin/python

'''
	Xingfan Zhang, 12/2023
	Woongkyu Jee, 12/203
'''

import os
import sys

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

def get_stdcif(path):
	
	with open(path,'r') as f:
		std_cif = transform_cif_to_standard(f)

	with open('std.cif','w') as f:
		for line in std_cif:
			f.write(line)
			f.write('\n')

if __name__ == "__main__":
	


	# Manual
	cif_file_path = '/work/e05/e05/wkjee/SolidSolution/Batteries/LiS/tfklmc_10_t1/result/A0/cryst.cif'

	with open(cif_file_path, "r") as f:
		std_cif = transform_cif_to_standard(f)

	#for line in std_cif:
	#	print(line)

	get_stdcif(cif_file_path)
	

