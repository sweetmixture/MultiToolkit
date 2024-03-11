# 03.2024 W.JEE
# KLMC Solid Soultion
#
# this script must be followed by using 'KLMC_SS_Screening.sh' 
#
#	e.g., 'KLMC_SS_Screening.sh' summarise successful files in 'summary' directory
#	! Feed the directory name '/summary' to the variable '_summary'
#	! Execute this script where '/summary' is included
#
# Core->Shell converted inputfiles to '_newrun'

import os
from concurrent.futures import ProcessPoolExecutor

# USER DEFINE ----
_summary = 'summary'
_header_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/new_header'		# gulp header location - keywords + cell info
_footer_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/new_footer'		# gulp footer location - potential + optionwords
_header_lim = 10	# line counts for keywords 
_sta = 0			# sample starting tag e.g., A{_sta}
_max_value = 19501	# sample ending   tag
_max_threads = 32	# max cpus to use 
_Natoms = 72 + ?(any extra atom count)	# number of atoms in system
_newrun = 'tmprun'
# USEF DEFINE ----

def process_file(i):

	global _summary
	global _header_file, _footer_file
	global _header_lim
	global _sta, _max_value
	global _max_threads
	global _Natoms
	global _newrun

	header_lim = _header_lim
	root = os.getcwd()
	header_file = _header_file
	footer_file = _footer_file
	Natoms = _Natoms
	headN = Natoms + header_lim

	with open(f"{root}/{_summary}/A{i}.gin", "r") as target_input:
		lines = target_input.readlines()
		# slicing only geometry part
		geometry_lines = lines[:headN]
		geometry_lines = geometry_lines[header_lim:]

	# writing temporal geometry file (runtime)
	with open("geometry", "w") as geometry_file:
		geometry_file.writelines(geometry_lines)

	with open(f"{header_file}", "r") as header_content, \
		 open(f"{root}/{_newrun}/A{i}.gin", "w") as output_file, \
		 open(f"{footer_file}", "r") as footer_content:

		output_file.write(header_content.read())
		output_file.writelines(geometry_lines)
		output_file.write(footer_content.read())

	print(f"progressing ... {i}")

if __name__ == "__main__":

	sta = _sta
	max_value = _max_value
	os.makedirs(f'{_newrun}', exist_ok=True)

	with ProcessPoolExecutor(max_workers=_max_threads) as executor:
		executor.map(process_file, range(sta, max_value + 1))

	#os.rename("newrun.log", f"{os.getcwd()}/newrun/newrun.log")

	# Cleaning
	os.remove("geometry")

