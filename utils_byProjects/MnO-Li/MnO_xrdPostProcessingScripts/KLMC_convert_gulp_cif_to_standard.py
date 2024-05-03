#
#   03.2024 W.Jee 
#
#   KLMC Solid Solution: scripts for production phase
#
'''
	Xingfan Zhang, 12/2023
	Woongkyu Jee, 12/203

	* converting nosym/full GULP cif file to standar cif file for futher XRD analysis
'''
# USER DEFINE ----
_gulp_cif_filename = 'cryst.cif'     # this may vary by user's setting of KLMC input file -> see output cif command option word in GULP
_gulp_klmc_tf_prefix = 'A'           # klmc taskfarming gulp run directory prefix, e.g., A0, A1, A2, ... A9999.
_gulp_converted_filename = 'std.cif'   # expected converted output cif file name
# USER DEFINE ----
#
# * IMPORTANT * see line number 98
# if any dummy atom is used, e.g., different atom name to represent different oxidation state -> their name must be replaced back to normal
# such replacement could be done by the line in 98. This is user's responsibility

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
					  if filename == f"{_gulp_cif_filename}" and root.startswith(f"./{_gulp_klmc_tf_prefix}")]

total_files = len(files_to_transform)
print(f"Found {total_files} files to transform.")

from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def process_file(file_path):
	with open(file_path, "r") as file_a:
		#content_a = file_a.readlines()

		'''
			custom .. wkjee 31.01.2024
			for the LiMnO2 project purpose ... replace dummy reduced Mn (Tc) -> Mn
		'''
		# USER DEFINE ----
		# CONVERTING DUMMY ATOM NAME BACK TO NORMAL !!!
		content_a = [line.replace('Tc', 'Mn') for line in file_a.readlines()]
		# USER DEFINE ----

	transformed_a = transform_cif_to_standard(content_a)

	output_path = os.path.join(os.path.dirname(file_path), f"{_gulp_converted_filename}")
	with open(output_path, "w") as file_b:
		file_b.write("\n".join(transformed_a))

# Parallelize file processing
with ProcessPoolExecutor() as executor:
	futures = []
	for file_path in files_to_transform:
		futures.append(executor.submit(process_file, file_path))
	
	# Track progress with tqdm
	for future in tqdm(futures, total=len(files_to_transform), desc="Converting CIF"):
		future.result()  # Wait for each task to complete


print("Transformation complete!")
