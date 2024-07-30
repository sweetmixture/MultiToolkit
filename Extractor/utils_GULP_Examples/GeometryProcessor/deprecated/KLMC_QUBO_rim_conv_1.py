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

	_MAX_ITEM = 10
	_gtol = 0.00001
	dir_path = os.getcwd()

	def process_file(file_id):
		gdir  = 'A' + str(file_id)
		gpath = os.path.join(dir_path,gdir)
		gfile = 'gulp_klmc.gout'
		gpath = os.path.join(gpath,gfile)
		lres, res = get_gulp_output(gpath,_gtol)


		if lres :
			#res.update({'taskid': file_id})
			return file_id, res  # res is already 'json' format (dict)
		else:
			return None


	klmc_qubo_res = {}
	with ProcessPoolExecutor(max_workers=64) as executor:

	    for result in executor.map(process_file,range(_MAX_ITEM)):      # execute 'process_file'
	        if result:  # if result != None
	            klmc_qubo_res[result[0]] = result[1]
	            print(f"\r Processed {len(klmc_qubo_res)} out of {_MAX_ITEM} directories ({len(klmc_qubo_res) / _MAX_ITEM * 100:.2f}% complete).",end="")
	#
	# Remove None
	# 
	# results = [res for res in results if res is not None]

	_pklfile = 'TestGen'
	
	with open(f'{_pklfile}.pkl','wb') as f:
 	   pickle.dump(klmc_qubo_res,f)

