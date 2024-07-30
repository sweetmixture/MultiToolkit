#
# WKJEE 07.2024
#

from Extractor.GULP import ExtractGULP
from concurrent.futures import ProcessPoolExecutor
import os,sys
import pandas as pd
import pickle

#
# for conv calculations only!  WKJEE
# 
def get_gulp_output(fname,__gtol):

	root = os.getcwd()
	fpath = os.path.join(root,fname)

	eg = ExtractGULP()
	fcheck = eg.set_output_file(fpath)

	if fcheck :

		finish_check = eg.check_finish_normal()
		gnorm_check, gnorm = eg.get_final_gnorm(gnorm_tol=__gtol)
	
		checklist = []
	
		if finish_check == True and gnorm_check == True:

			# * Initial Config
			l_init_energy  , init_energy  = eg.get_initial_energy()
			l_init_energyf , init_energyf = eg.get_initial_energy_full()
			l_init_lvec    , init_lvec    = eg.get_initial_lvectors()
			l_init_config  , init_config  = eg.get_initial_frac_cosh()
			# checklist
			checklist.append(l_init_energy)
			checklist.append(l_init_energyf)
			checklist.append(l_init_lvec)
			checklist.append(l_init_config)

			# * Final Config
			l_final_energy  , final_energy  = eg.get_final_energy()
			l_final_energyf , final_energyf = eg.get_final_energy_full()
			#l_final_lvec    , final_lvec    = eg.get_final_lvectors()		# CONV - does not have final lvectors
			l_final_config  , final_config  = eg.get_final_frac_cosh()
			# checklist
			checklist.append(l_final_energy)
			checklist.append(l_final_energyf)
			#checklist.append(l_final_lvec)
			checklist.append(l_final_config)

		else:
			eg.reset()
			return False, None

		if False in checklist:  # any fail(s) detected
			eg.reset()
			return False, None
		else:                   # all checklist True

			eg.reset()

			ret = { 
					'initial' : {
									'energy'			: init_energy,
									'energy_ip'			: init_energyf[0],
									'energy_long'		: init_energyf[3],
									'energy_long_real'  : init_energyf[1],
									'energy_long_imag'  : init_energyf[2],

									'lattice_vectors'   : init_lvec,
									'config'			: init_config,
								},

					'final'   : {
									'energy'			: final_energy,
									'energy_ip'			: final_energyf[0],
									'energy_long'		: final_energyf[3],
									'energy_long_real'  : final_energyf[1],
									'energy_long_imag'  : final_energyf[2],

									'lattice_vectors'   : init_lvec,	# note! for conv it has to be init_lvec
									'config'			: final_config,
								},
					}

			return True, ret



if __name__ == '__main__':

	_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/li1/A0/gulp_klmc.gout'
	_gtol = 0.00001

	lres, res = get_gulp_output(_file,_gtol)

	# ------
	ires = res['initial']
	print(f'* INITIAL --------')
	print(f"{ires['energy']}")
	print(f"{ires['energy_ip']}")
	print(f"{ires['energy_long_real']}")
	print(f"{ires['energy_long_imag']}")
	print(f"{ires['energy_long']}")
	lvec = ires['lattice_vectors']
	for vec in lvec:
		print(vec)
	config = ires['config']
	for atom in config:
		print(atom)

	# ------
	fres = res['final']
	print(f'* FINAL --------')
	print(f"{fres['energy']}")
	print(f"{fres['energy_ip']}")
	print(f"{fres['energy_long_real']}")
	print(f"{fres['energy_long_imag']}")
	print(f"{fres['energy_long']}")
	lvec = fres['lattice_vectors']
	for vec in lvec:
		print(vec)
	config = fres['config']
	for atom in config:
		print(atom)


