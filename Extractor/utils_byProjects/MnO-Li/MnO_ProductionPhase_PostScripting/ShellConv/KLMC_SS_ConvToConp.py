# 03.2024 W.JEE
# KLMC Solid Soultion
#
# this script must be followed by using 'KLMC_SS_Screening.sh' 
#
#	e.g., 'KLMC_SS_Screening.sh' summarise successful files in 'summary' directory
#	! Feed the directory name '/summary' to the variable '_summary'
#	! Execute this script where '/summary' is included
#
# Converted inputfiles to '_newrun'

import os
from concurrent.futures import ProcessPoolExecutor

# USER DEFINE ----
_summary = 'summary'
_header_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/new_header'		  # gulp header location - keywords + cell info
_footer_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/new_footer_freq'   # gulp footer location - potential + optionwords
_sta = 0			  # sample starting tag e.g., A{_sta}
_max_value = 1000	  # sample ending	tag
_max_threads = 32	  # max cpus to use
_newrun = 'tmprun'
# USER DEFINE ----

def process_file(i):

	global _summary
	global _header_file, _footer_file
	global _newrun

	root = os.getcwd()

	header_file = _header_file
	footer_file = _footer_file

	with open(f"{root}/{_summary}/A{i}.gin", "r") as target_input:
		lines = target_input.readlines()

		end_line   = None
		for l,line in enumerate(lines):
			if 'total' in line:
				end_line = l
				break

		geometry_lines = lines[:l]
		geometry_lines = geometry_lines[5:]

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

	#os.rename("newrun.log", f"{os.getcwd()}/newrun_freq/newrun.log")
	# Cleaning
	os.remove("geometry")

