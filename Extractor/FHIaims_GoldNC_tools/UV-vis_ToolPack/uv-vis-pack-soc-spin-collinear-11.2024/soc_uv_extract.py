#
#   UV-VIS FHIaims analyser
#
#   07.2024 WKJEE
#
#   utility script: Extracting state_i, eval_i, state_f, eval_f, dipole_transition_intensity
#
import sys

file = 'uv_mpipy.out'                # uv-vis simulator standard output
pattern = '*loading finished*'       # keyword for searching (DO NOT CHANGE THIS!)

with open(file,'r') as f:

	for line in f:
		if pattern in line:
	
			lis = line.strip().split()
			# Example searched line : '3109', '-6.219205', '3119', '-3.195316', '*loading', 'finished*', '786211.196106571',

			istate = int(lis[0])
			fstate = int(lis[2])

			istate_eval = float(lis[1])
			fstate_eval = float(lis[3])

			uv_int = float(lis[6])

			print(f'{istate:6d}{fstate:6d}{istate_eval:16.8f}{fstate_eval:16.8f}{uv_int:24.12f}')
