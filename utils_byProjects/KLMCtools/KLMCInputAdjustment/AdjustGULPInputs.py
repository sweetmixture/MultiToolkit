# 05.2024 W.JEE
# Generic File Name Changer
# Usage: running KLMC task-farming interface when loading GULP input files from disk
#     * adjusting 'maxcyc', 'using rfo optimiser' in inputfiles (instead of re-running KLMC)
#
# run this python script in KLMC '/run' directory (where sampled input files are saved)
#
import os
import re
from multiprocessing import Pool
from tqdm import tqdm

# USER DEFINE =====
_TARGET_FILE_PREFIX = 'X'
_FINAL_FILE_PREFIX = 'A'
_TASK_ID_START = 0
_TASK_ID_END = 3999

# CONTROLS : 'maxcyc' / 'switch rfo _rftol'
_ifmaxcyc = True
_maxcyc = 2000
_ifrfo = False
_rfotol = '0.00005'
# USER DEFINE ======

def process_file(i):

	old_filename = f"{_TARGET_FILE_PREFIX}{i}.gin"
	new_filename = f"{_FINAL_FILE_PREFIX}{i}.gin"
	
	# Rename the file
	try:
		os.rename(old_filename, new_filename)
	except:
		pass
	
	# Modify the file contents
	with open(new_filename, 'r+') as file:
		lines = file.readlines()
		updated_lines = []
		for line in lines:

			# resetting maxcyc
			if _ifmaxcyc :
				if 'maxcyc' in line:
					line = f'maxcyc opt {_maxcyc}\n'
				#if re.search(r'maxcyc opt\b', line):
				#	line = re.sub(r'(maxcyc opt)\b.*$', r'\1  2000', line.rstrip()) + '\n'	# Replace the line

			# turning on/off rfo
			if not _ifrfo :
				if 'switch rfo' in line:
					line = f'#switch rfo {_rfotol}\n'
			if _ifrfo :
				if 'switch rfo' in line:
					line = f'switch rfo {_rfotol}\n'

			updated_lines.append(line)
		
		file.seek(0)
		file.truncate()
		file.writelines(updated_lines)
	
	return i

if __name__ == "__main__":

	start_i = _TASK_ID_START
	end_i = _TASK_ID_END	

	num_processes = os.cpu_count() // 4  # Use a quarter of available CPU cores
	if num_processes == 0:
		num_processes = 1

	file_range = range(start_i, end_i + 1)	# Range of i values to process
	
	with Pool(num_processes) as pool, tqdm(total=len(file_range)) as pbar:
		for _ in pool.imap_unordered(process_file, file_range):
			pbar.update(1)
	
	print("All processes completed successfully.")
