# 05.2024 W.JEE
# Generic File Name Changer
# Usage: running KLMC task-farming interface when loading GULP input files from disk
#
# run this python script in KLMC '/run' directory (where sampled input files are saved)
#
import os
from multiprocessing import Pool
from tqdm import tqdm

# USER DEFINE =====
_TARGET_FILE_PREFIX = 'X'
_FINAL_FILE_PREFIX = 'A'
_TASK_ID_START = 0
_TASK_ID_END = 3999
# USER DEFINE ======

def process_file(i):

	global _TARGET_FILE_PREFIX, _FINAL_FILE_PREFIX

	old_filename = f"{_TARGET_FILE_PREFIX}{i}.gin"
	new_filename = f"{_FINAL_FILE_PREFIX}{i}.gin"
	
	os.rename(old_filename, new_filename)
	
	with open(new_filename, 'r+') as file:
		lines = file.readlines()
		updated_lines = [line for line in lines if 'output xyz' not in line]
		file.seek(0)
		file.truncate()
		file.writelines(updated_lines)
	
	return i

if __name__ == "__main__":

	start_i = _TASK_ID_START  # Starting value of i
	end_i = _TASK_ID_END  # Ending value of i

	num_processes = os.cpu_count() // 4  # Use a quarter of available CPU cores
	if num_processes == 0:
		num_processes = 1

	file_range = range(start_i, end_i + 1)	# Range of i values to process
	
	with Pool(num_processes) as pool, tqdm(total=len(file_range)) as pbar:
		for _ in pool.imap_unordered(process_file, file_range):
			pbar.update(1)
	
	print("All processes completed successfully.")

